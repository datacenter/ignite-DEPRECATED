from __future__ import absolute_import
import os
import requests
import json


def build_nxapi_url(switch_ip):
    url = 'http://'+switch_ip+'/ins'
    return url


def build_scp_string(image_user, image_ip, image_path):
    scp_string = 'scp://'+image_user+'@'+image_ip+image_path
    return scp_string


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


def handle_nxapi_error(swicth, image, command, timeout):
    if command[2] == 'install':
        return 'FAILUREE'
    else:
        return 'CONTINUE'


def update_os_image_single_switch(switch, task):
    image = task["image"]
    url = build_nxapi_url(switch["ip"].split('/')[0])
    scp_string = build_scp_string(image["user"], image["ip"], image["path"])
    image_name = image["path"].split(r'/')[-1]
    myheaders = {'content-type': 'application/json-rpc'}
    commands = []
    commands.append(['terminal dont-ask', 7, 'set'])
    commands.append(['terminal password ' + image["pwd"], 7, ''])
    commands.append(['del bootflash:' + image_name + 'no-prompt', 70, ''])
    commands.append(['copy ' + scp_string + ' bootflash:' + image_name + ' vrf management', 300, 'scp'])
    commands.append(['no terminal password', 7, 'set'])
    commands.append(['copy running-config startup-config', 7, 'copy-config'])
    commands.append(['install all nxos bootflash:' + image_name, 500, 'install'])
    #commands.append(['terminal dont-ask', 7, 'set'])
    #commands.append(['sh run', 7, 'set'])
    #commands.append(['no terminal dont-ask', 7, 'set'])
    payload = []
    payload_temp = []
    status = {"status":"","log":""}
    template = get_nxapi_template()
    for command in commands:
        template['params']['cmd'] = command[0]
        print command[0]
        time_out = command[1]
        payload.append(template)
        try:
            response = requests.post(url, data=json.dumps(payload),
                                     headers=myheaders,
                                     auth=(switch["user"], switch["pwd"]),
                                     timeout=time_out).json()
            print response
            if 'error' in response:
                #handle errors here
                print 'error occured while running ', command
                ret = handle_nxapi_error(switch, image, command, timeout=0)
                if ret == 'FAILURE':
                    status["status"]=ret
                    status["log"]=response["error"]
                    return status
        except requests.exceptions.Timeout:
            print 'timeout occured while running', command
            #return handle_nxapi_error(switch, image, command, timeout=1)
            status["status"]='FAILURE'
            status["log"]="Timed Out"
            return status
            break
        except Exception as e:
            print e, ' while running ', command
            status["status"]='FAILURE'
            status["log"]=str(e)
            return status
            #return handle_nxapi_error(switch, image, command, timeout = 0)
            break
        payload.pop()
    status["status"]='SUCCESS'
    return status
