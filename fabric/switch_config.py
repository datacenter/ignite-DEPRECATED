from django.core.servers.basehttp import FileWrapper
from django.db.models import Max
from django.http import HttpResponse
import json
import os
import requests
import string

from constants import *
from models import Switch, SwitchConfig
from ignite.settings import MEDIA_ROOT
from utils.exception import IgniteException


import logging
logger = logging.getLogger(__name__)

def build_nxapi_url(switch_ip):
    url = 'http://'+switch_ip+'/ins'
    return url

def get_nxapi_template():
    d = {
        "jsonrpc": "2.0",
        "method": "cli_ascii",
        "params": {
            "cmd": "",
            "version": 1
        },
        "id": 1
    }
    return d


def send_request(sw_data):
    try:
        logger.debug(str(sw_data))
        url = build_nxapi_url(sw_data['mgmt_ip'])
        logger.debug(url)
        myheaders = {'content-type': 'application/json-rpc'}
        command = 'show running-config'
        payload = list()
        status = {"status":"","log":""}
        template = get_nxapi_template()
        template['params']['cmd'] = command
        payload.append(template)
        logger.debug(str(payload))

        try:
            response = requests.post(url, data=json.dumps(payload),
                                          headers=myheaders,timeout=7,
                                          auth=(sw_data['username'], sw_data['password'])
                                    ).json()
            return response

        except requests.exceptions.Timeout:
            logs = 'timeout occured while running ' + command
            logger.error(logs)
            raise IgniteException(ERR_SWITCH_CONFIG_FAILED)
    except Exception as e:
        logger.error(e)
        raise IgniteException(ERR_SWITCH_CONFIG_FAILED)


def remove_temp(filename):
    try:
        os.remove(filename)
    except Exception as e:
        logger.info(e)


def update_file(id, resp):
    obj = SwitchConfig.objects.get(id=id)
    obj.path.delete(save=False)
    temp_path = os.path.join(MEDIA_ROOT, 'switch', 'temp.cfg')
    fo = open(temp_path, 'w')
    for line in resp['result']['msg']:
        fo.write(line)
    fo.close()
    fo = open(temp_path, 'r')
    from django.core.files.base import File
    obj.path = File(fo)
    obj.save()
    fo.close()
    remove_temp(temp_path)

def create_file(switch, version, username, response):
    logger.debug(str(switch))
    logger.debug(str(version))
    obj = SwitchConfig()
    obj.switch = switch
    obj.updated_by = username
    if not version:
        obj.name = "%s.1.cfg" % (str(switch.id)) 
        obj.version = 1
        obj.save()
    else:
        obj.name = "%s.%s.cfg" % (str(switch.id), str(version+1)) 
        obj.version = version + 1
        obj.save()
    update_file(obj.id, response)
    return obj.name


def get_file(filename):
    path = os.path.join(MEDIA_ROOT,'switch', filename)

    try:
        wrapper = FileWrapper(file(path))
    except:
        raise IgniteException(ERR_SWITCH_CONFIG_FAILED)

    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path)
    return response


def pull_switch_config(data, fid, switch_id, username=''):
    switch = Switch.objects.get(id=switch_id, topology_id=fid)
    data['id'] = switch.id
    data['mgmt_ip'] = switch.mgmt_ip.split('/')[0]

    response = send_request(data)
    temp_path = os.path.join(MEDIA_ROOT, 'switch', 'temp.cfg')

    if not response:
        raise IgniteException(ERR_SWITCH_CONFIG_FAILED)

    objs = SwitchConfig.objects.filter(switch=switch).aggregate(Max('version'))
    if not objs['version__max']:
        new_name = create_file(switch, 0, username, response)
        remove_temp(temp_path)
        return get_file(new_name)

    objects = SwitchConfig.objects.filter(switch=switch).filter(version=objs['version__max'])
    old_file = objects[0].name
    version = objects[0].version
    sw_config_id = objects[0].id
    f_path = os.path.join(MEDIA_ROOT, 'switch', old_file)
    logger.debug(f_path)
    same = True
    try:
        tem_fo = open(temp_path, 'w')
        tem_fo.write(response['result']['msg'])
        tem_fo.close()
        tem_fo = open(temp_path, 'r')
        fo = open(f_path, 'r')
        fo_old = fo.readlines()
        del fo_old[1]
        fo_new = tem_fo.readlines()
        logger.debug(str(len(fo_new)))
        logger.debug(str(len(fo_old)))
        del fo_new[1]
        for line1, line2 in zip(fo_old, fo_new):
            if not line1 == line2:
                same = False
                break
    except Exception as e:
        logger.error(e)
        remove_temp(temp_path)
        raise IgniteException(ERR_SWITCH_CONFIG_FAILED)

    if same:
        obj = SwitchConfig.objects.get(id=sw_config_id)
        obj.username = username
        obj.save()
        remove_temp(temp_path)
        return get_file(obj.name)
    else:
        new_name = create_file(switch,version, username, response)
        remove_temp(temp_path)
        return get_file(new_name)


def wrap_config_file(name):
    path = os.path.join(MEDIA_ROOT,"switch", name)
    if not os.path.isfile(path):
        IgniteException(ERR_SWITCH_CONFIG_NOT_AVAILABLE)

    try:
        wrapper = FileWrapper(file(path))
    except:
        raise IgniteException(ERR_SWITCH_CONFIG_FAILED)
    response = HttpResponse(wrapper, content_type='text/plain')
    response['Content-Length'] = os.path.getsize(path)
    return response


def get_latest_version(sid):
    objs = SwitchConfig.objects.filter(switch_id=sid)
    ver = objs.aggregate(Max('version'))
    logger.debug("show config = " + str(ver))
    if not objs.filter(version=ver['version__max']):
        raise IgniteException(ERR_SWITCH_CONFIG_NOT_AVAILABLE)

    sw_cfg = objs.filter(version=ver['version__max'])[0]
    return sw_cfg.name


def get_switch_config_latest(fid, sid):
    if Switch.objects.filter(id=sid, topology_id=fid):
        return wrap_config_file(get_latest_version(sid))
    else:
        logger.error(ERR_FABRIC_SWITCH_DIFFERENT)
        raise IgniteException(ERR_FABRIC_SWITCH_DIFFERENT)


def clear_switch_config(sw_id):
    logger.debug(type(sw_id))
    config_list = SwitchConfig.objects.filter(switch_id=int(sw_id))
    try:
        for cfg in config_list:
            cfg.path.delete(save=False)
            cfg.delete()
    except Exceptin as e:
        logger.error(e)


def get_switch_config_list(fid, sid):
    if Switch.objects.filter(id=sid, topology_id=fid):
        configs = SwitchConfig.objects.filter(switch_id=sid).order_by('version')
        return configs
    else:
        logger.error(ERR_FABRIC_SWITCH_DIFFERENT)
        raise IgniteException(ERR_FABRIC_SWITCH_DIFFERENT)


def get_switch_config(fid, sid, id):
    if Switch.objects.filter(id=sid, topology_id=fid):
        config = SwitchConfig.objects.get(id=id, switch_id=sid)
        return wrap_config_file(config.name)
    else:
        logger.error(ERR_FABRIC_SWITCH_DIFFERENT)
        raise IgniteException(ERR_FABRIC_SWITCH_DIFFERENT)
