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
from fabric.build import build_config, build_switch_config
from fabric.fabric import search_fabric, get_switch_workflow, get_switch_image, get_switch_feature_profile
from fabric.models import Switch
from ignite.conf import IGNITE_IP, IGNITE_USER, IGNITE_PASSWORD
from ignite.conf import REMOTE_SYSLOG_PATH, LOG_LINE_COUNT
from ignite.settings import REPO_PATH, PKG_PATH, YAML_LIB
from models import SwitchBootDetail
from utils.exception import IgniteException
from workflow.constants import ACCESS_PROTOCOLS, BOOTSTRAP_WORKFLOW_ID
from workflow.workflow import build_workflow, get_workflow


import logging
logger = logging.getLogger(__name__)


def ignite_request(request):
    serial_number = request[SERIAL_NUM]
    switch, match_type = search_fabric(request)

    if switch:

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

        # fetch switch workflow
        wf = get_switch_workflow(switch)

        # fetch switch image
        image = get_switch_image(switch)

        logger.debug("Build workflow")
        cfg_file = os.path.join(REPO_PATH + str(switch.id) + CFG_FILE_EXT)
        wf_file = os.path.join(REPO_PATH + str(switch.id) + YAML_FILE_EXT)

        with open(wf_file, 'w') as output_fh:
            output_fh.write(yaml.safe_dump(build_workflow(wf,
                                                          image,
                                                          cfg_file,
                                                          serial_number),
                                           default_flow_style=False))

        update_boot_detail(switch,
                           match_type=match_type,
                           boot_status=BOOT_PROGRESS,
                           boot_time=timezone.now())

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
                           boot_status=BOOT_PROGRESS)

        logger.debug("Build workflow")
        cfg_file = os.path.join(REPO_PATH + str(switch.id) + CFG_FILE_EXT)
        wf_file = os.path.join(REPO_PATH + str(switch.id) + YAML_FILE_EXT)

        with open(wf_file, 'w') as output_fh:
            output_fh.write(yaml.safe_dump(build_workflow(wf,
                                                          rule.image,
                                                          cfg_file,
                                                          serial_number),
                                           default_flow_style=False))

        return _get_server_response(True, wf_file)

    return _get_server_response(False)


def update_boot_detail(switch, boot_status="",
                       match_type="",
                       discovery_rule=None,
                       boot_time=""):

    if not switch.boot_detail:
        boot_detail = SwitchBootDetail()
    else:
        boot_detail = switch.boot_detail

    if boot_status:
        boot_detail.boot_status = boot_status

    if match_type:
        boot_detail.match_type = match_type

    if discovery_rule:
        boot_detail.discovery_rule = discovery_rule.id

    if boot_time:
        boot_detail.boot_time = boot_time

    boot_detail.save()
    switch.boot_detail = boot_detail
    switch.save()


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
    response[FILE] = yaml_file
    response[ACCESS_METHOD] = ACCESS_PROTOCOLS[2]
    response[YAML_PATH] = os.path.join(PKG_PATH, YAML_LIB)
    return response


def get_all_booted_switches():
    return Switch.objects.filter(boot_detail__isnull=False)


def update_boot_status(data):
    serial_num = data[SERIAL_NUM]
    status = data[STATUS]
    try:
        switch = Switch.objects.get(serial_num=serial_num)
        if status:
            update_boot_detail(switch, boot_status=BOOT_SUCCESS)
        else:
            update_boot_detail(switch, boot_status=BOOT_FAIL)
    except Switch.DoesNotExist:
        raise IgniteException(ERR_SERIAL_NUM_MISMATCH)


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
        except:
            return []

        start_string_handler = None
        lines = sys_fo.readlines()
        sys_fo.close()

        if is_common_log:
            for line in lines:
                words = line.split()
                if key1 == words[LOG_SEARCH_COL]:
                    partial_log_file.append(line)
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
    serial_num = str(switch.boot_detail.serial_number)
    file_name_list = getfile_list(syslog_path)
    if not switch.boot_detail:
        raise IgniteException(ERR_SWITCH_NOT_BOOTED)

    file_with_switch = [REMOTE_SYSLOG_PATH + serial_num + '.log']
    log_file = []
    try:
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
        except:
            return []
    except:
        raise IgniteException(ERR_FAILED_TO_READ_SYSLOGS)
    return []
