import json
import os
from django.db import IntegrityError
from django.utils import timezone
import glob
import gzip
import yaml

from config.profile import build_config_profile
from constants import *
import discovery.discoveryrule as discoveryrule
from fabric.constants import SERIAL_NUM, SERIAL_NUMBER, NEIGHBOR, ERR_SERIAL_NUM_IN_USE
from fabric.constants import POAP_CONFIG, RUNNING_CONFIG, DISCOVERY
from fabric.build import build_config, build_switch_config
from fabric.fabric import search_fabric, get_switch_workflow
from fabric.fabric import get_switch_image, get_switch_feature_profile
from fabric.models import Switch
from fabric.switch_config import get_latest_version
from switch.models import SwitchModel
from ignite.conf import IGNITE_IP, IGNITE_USER, IGNITE_PASSWORD, SYSLOG_PATH
from ignite.conf import REMOTE_SYSLOG_PATH, LOG_LINE_COUNT, ACCESS_PROTOCOL
from ignite.settings import REPO_PATH, PKG_PATH, YAML_LIB, SWITCH_CONFIG_PATH
from models import SwitchBootDetail
from utils.exception import IgniteException
from workflow.constants import PROTO_SCP, PROTO_TFTP, PROTO_HTTP, PROTO_SFTP
from workflow.constants import ACCESS_PROTOCOLS, BOOTSTRAP_WORKFLOW_ID
from workflow.workflow import build_workflow, get_workflow


import logging
logger = logging.getLogger(__name__)


def get_cfg_file_path(path, cfg, file_path):
    if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
        cfg_file = os.path.join(path, cfg)
    elif ACCESS_PROTOCOL == PROTO_HTTP:
        cfg_file = os.path.join(DOWNLOAD_URL, CONFIG, cfg)
    else:
        cfg_file = os.path.join(file_path, cfg)
    return cfg_file


def ignite_request(request):
    if ACCESS_PROTOCOL not in ACCESS_PROTOCOLS:
        msg = ERR_PROTO_NOT_FOUND + "- " + ACCESS_PROTOCOL
        return _get_server_response(False, err_msg=msg)

    serial_number = request[SERIAL_NUM]
    model_type = request[MODEL_TYPE]
    switch, match_type = search_fabric(request)
    if switch:
        logger.info("config type - " + switch.config_type)
        cfg_file = None
        if switch.config_type == POAP_CONFIG:
            if (switch.topology.feature_profile or
                get_switch_feature_profile(switch)):
                logger.debug("Switch have feture profiles applied")
                build_config(switch.topology.id)
            else:
                # delete cfg file
                try:
                    os.remove(os.path.join(REPO_PATH + str(switch.id) + '.cfg'))
                except OSError as e:
                    pass
                # build new cfg
                build_switch_config(switch)

            cfg_file = str(switch.id) + CFG_FILE_EXT

            cfg_file = get_cfg_file_path(REPO_PATH, cfg_file, FILE_REPO_PATH)
            if not cfg_file:
                logger.error(ERR_CFG_NOT_FOUND)
                return _get_server_response(False,
                                            err_msg=ERR_CFG_NOT_FOUND)
            logger.info("config file found for " + switch.config_type)

        elif switch.config_type == RUNNING_CONFIG:
            running_config = get_latest_version(switch.id)

            cfg_file = get_cfg_file_path(SWITCH_CONFIG_PATH, running_config, FILE_SWITCH_PATH)
            if not cfg_file:
                logger.error(ERR_CFG_NOT_FOUND)
                return _get_server_response(False,
                                            err_msg=ERR_CFG_NOT_FOUND)
            logger.info("config file found for " + switch.config_type)

        # fetch switch workflow
        wf = get_switch_workflow(switch)

        # fetch switch image
        image = get_switch_image(switch)

        wf_file = str(switch.id) + YAML_FILE_EXT

        logger.debug("Build workflow")

        with open(os.path.join(REPO_PATH, wf_file), 'w') as output_fh:
            output_fh.write(yaml.safe_dump(build_workflow(wf,
                                                          image,
                                                          cfg_file,
                                                          serial_number),
                                           default_flow_style=False))
        update_boot_detail(switch,
                           match_type=match_type,
                           boot_status=BOOT_PROGRESS,
                           boot_time=timezone.now(),
                           model_type=model_type)


        #update switch serial number
        if switch.serial_num != serial_number:
            logger.debug("Received serial number % s\
                         configured serial number % s"
                         % (serial_number, switch.serial_num))
            try:
                discoveryrule.find_duplicate([serial_number])
            except IgniteException:
                logger.debug(ERR_SERIAL_NUM_IN_USE)
                return _get_server_response(False,
                                            err_msg=ERR_SERIAL_NUM_IN_USE)

            switch.serial_num = serial_number
            switch.save()

        if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
            wf_file = os.path.join(REPO_PATH, wf_file)
        elif ACCESS_PROTOCOL == PROTO_HTTP:
            wf_file = os.path.join(DOWNLOAD_URL, YAML, wf_file)
        else:
            wf_file = os.path.join(FILE_REPO_PATH, wf_file)

        return _get_server_response(True, wf_file)

    logger.debug("No match found in fabric")

    rule = discoveryrule.match_discovery_rules(request)

    wf = None

    if rule:
        try:
            switch = Switch.objects.get(name=serial_number,
                                        topology__isnull=True)
        except Switch.DoesNotExist:
            switch = Switch()
            switch.name = serial_number
            switch.serial_num = serial_number
            switch.save()

        if rule.workflow:
            wf = rule.workflow
        else:
            wf = get_workflow(BOOTSTRAP_WORKFLOW_ID)

        logger.debug("Discovery rule match- workflow: %s, config: %s"
                     % (wf.name, rule.config.name))

        # delete cfg file
        try:
            os.remove(os.path.join(REPO_PATH + str(switch.id) + '.cfg'))
        except OSError as e:
                pass

        # build new cfg
        build_switch_config(switch, switch_cfg=rule.config)

        if rule.match == SERIAL_NUM:
            match_type = SERIAL_NUMBER
        else:
            match_type = NEIGHBOR

        update_boot_detail(switch,
                           match_type=match_type,
                           discovery_rule=rule,
                           boot_time=timezone.now(),
                           boot_status=BOOT_PROGRESS,
                           model_type=model_type)

        cfg_file = str(switch.id) + CFG_FILE_EXT
        wf_file = str(switch.id) + YAML_FILE_EXT

        logger.debug("Build workflow")
        if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
            cfg_file = os.path.join(REPO_PATH, cfg_file)
        elif ACCESS_PROTOCOL == PROTO_HTTP:
            cfg_file = os.path.join(DOWNLOAD_URL, CONFIG, cfg_file)
        else:
            cfg_file = os.path.join(FILE_REPO_PATH, cfg_file)

        with open(os.path.join(REPO_PATH, wf_file), 'w') as output_fh:
            output_fh.write(yaml.safe_dump(build_workflow(wf,
                                                          rule.image,
                                                          cfg_file,
                                                          serial_number),
                                           default_flow_style=False))

        if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
            wf_file = os.path.join(REPO_PATH, wf_file)
        elif ACCESS_PROTOCOL == PROTO_HTTP:
            wf_file = os.path.join(DOWNLOAD_URL, YAML, wf_file)
        else:
            wf_file = os.path.join(FILE_REPO_PATH, wf_file)

        return _get_server_response(True, wf_file)

    return _get_server_response(False)


def update_boot_detail(switch, boot_status="",
                       match_type="",
                       discovery_rule=None,
                       boot_time="",
                       model_type=""):

    if not switch.boot_detail:
        boot_detail = SwitchBootDetail()
        old_status = None
    else:
        boot_detail = switch.boot_detail
        old_status = switch.boot_detail.boot_status

    if boot_status:
        boot_detail.boot_status = boot_status

    if match_type:
        boot_detail.match_type = match_type

    if discovery_rule:
        boot_detail.discovery_rule = discovery_rule.id

    if boot_time:
        boot_detail.boot_time = boot_time

    if model_type:
        boot_detail.model_type = model_type

    boot_detail.save()
    switch.boot_detail = boot_detail
    switch.save()
    logger.debug(str(old_status)+" " + str(model_type) +" " + str(boot_status) +" " + str(match_type))
    if model_type:
        update_switch_model(old_status, boot_status, model_type, match_type)
    elif match_type == DISCOVERY:
        model_type = SwitchModel.objects.get(pk=1).name
        update_switch_model(BOOT_PROGRESS, boot_status, model_type, match_type)
    else:
        update_switch_model(old_status, boot_status, boot_detail.model_type, match_type)


def _get_server_response(status, yaml_file=None, err_msg=""):
    response = dict()
    response[STATUS] = status

    if not status:

        if err_msg:
            response[ERR_MSG] = err_msg
            return response

        response[ERR_MSG] = ERR_NO_RESPONSE
        return response

    response[SERVER_IP] = IGNITE_IP
    response[SERVER_USER] = IGNITE_USER
    response[SERVER_PASSWORD] = IGNITE_PASSWORD
    response[ACCESS_METHOD] = ACCESS_PROTOCOL
    response[FILE] = yaml_file
    if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
        response[YAML_PATH] = os.path.join(PKG_PATH, YAML_LIB)
    elif ACCESS_PROTOCOL == PROTO_HTTP:
        response[YAML_PATH] = os.path.join(DOWNLOAD_URL, PKG_DIR, YAML_LIB)
    else:
        response[YAML_PATH] = os.path.join(SCRIPT_DIR,
                                           PKG_DIR, YAML_LIB)
    return response


def get_all_booted_switches():
    return Switch.objects.filter(boot_detail__isnull=False)


def update_boot_status(data):
    serial_num = data[SERIAL_NUM]
    status = data[STATUS]
    model_type = data[MODEL_TYPE]
    try:
        switch = Switch.objects.get(serial_num=serial_num)
        if status:
            update_boot_detail(switch, boot_status=BOOT_SUCCESS)
        else:
            update_boot_detail(switch, boot_status=BOOT_FAIL)


    except Switch.DoesNotExist:
        raise IgniteException(ERR_SERIAL_NUM_MISMATCH)


def update_switch_model(old_status, boot_status, model_type, match_type):
    logger.debug("inside update_siwthc_model = " +str(old_status))
    try:
        switch_model = SwitchModel.objects.get(name=model_type)
    except SwitchModel.DoesNotExist:
        switch_model = SwitchModel.objects.get(pk=1)

    if boot_status == BOOT_PROGRESS:
        if not old_status == BOOT_PROGRESS:
            switch_model.boot_in_progress += 1
            switch_model.save()

    if boot_status == BOOT_SUCCESS:
        if old_status == BOOT_PROGRESS:
            switch_model.booted_with_success += 1
            if match_type != DISCOVERY:
                switch_model.boot_in_progress -= 1

    elif boot_status == BOOT_FAIL:
        if old_status == BOOT_PROGRESS:
            switch_model.booted_with_fail += 1
            switch_model.boot_in_progress -= 1

    switch_model.save()


def getfile_list(syslog_path):
    file_name_list = []
    try:
        for file_name in glob.glob(syslog_path):
            file_name_list.append(file_name)
        file_name_list.sort(reverse=True)
    except:
        pass
    return file_name_list


def preparelogs(file_name_list,  key1, is_common_log):
    for sysfile in file_name_list:
        partial_log_file = []
        sys_fo = None

        try:
            if sysfile.endswith('.gz'):
                sys_fo = gzip.open(sysfile, 'r')
            else:
                sys_fo = open(sysfile, 'r')
        except Exception as e:
            logger.error(str(e))
            return []

        start_string_handler = None
        lines = sys_fo.readlines()
        sys_fo.close()

        if is_common_log:
            for line in lines:
                try:
                    words = line.split()
                    if key1 == words[LOG_SEARCH_COL]:
                        partial_log_file.append(line)
                except:
                    pass
        else:
            partial_log_file = lines

        if partial_log_file:
            sys_len = len(partial_log_file)
            if sys_len > LOG_LINE_COUNT:
                return partial_log_file[sys_len-LOG_LINE_COUNT:]
            else:
                return partial_log_file
    return []


def get_logs(id):
    syslog_path = SYSLOG_PATH
    switch = Switch.objects.get(id=id)
    serial_num = str(switch.serial_num)
    file_name_list = getfile_list(syslog_path)
    if not switch.boot_detail:
        raise IgniteException(ERR_SWITCH_NOT_BOOTED)

    file_with_switch = [REMOTE_SYSLOG_PATH + serial_num + '.log']
    log_file = []
    try:
        logger.debug(str(file_name_list))
        log_file += [preparelogs(file_with_switch, serial_num, False)]
        log_file += [preparelogs(file_name_list, serial_num, True)]
        time_list = []
        for item in log_file:
            if item:
                time_list.append(item[0].split()[2])
        try:
            if len(time_list) > 1:
                if time_list[0] > time_list[1]:
                    return log_file[0]
                else:
                    return log_file[1]
            else:
                for item in log_file:
                    if item:
                        return item
        except Exception as e:
            logger.error(str(e))
            return []
    except Exception as e:
        logger.error(str(e))
        raise IgniteException(ERR_FAILED_TO_READ_SYSLOGS)
    return []
