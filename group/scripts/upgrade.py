from __future__ import absolute_import
import os
import requests
import json
import time


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


def handle_nxapi_error(command):
    if command[2] in [ 'system-install' , 'epld-install' ]:
        return 'FAILUREE'
    else:
        return 'CONTINUE'


def update_os_image_single_switch(switch, image):
    url = build_nxapi_url(switch["ip"])
    scp_string = build_scp_string(image["image_server_username"], image["image_server_ip"], image["system_image"])
    image_name = image["system_image"].split(r'/')[-1]
    myheaders = {'content-type': 'application/json-rpc'}
    commands = []
    commands.append(['terminal dont-ask', 7, 'set'])
    commands.append(['terminal password ' + image["image_server_password"], 7, ''])
    commands.append(['del bootflash:' + image_name + ' no-prompt', 70, ''])
    commands.append(['copy ' + scp_string + ' bootflash:' + image_name + ' vrf management', 300, 'scp'])
    commands.append(['no terminal password', 7, 'set'])
    commands.append(['copy running-config startup-config', 7, 'copy-config'])
    commands.append(['install all nxos bootflash:' + image_name, 500, 'system-install'])
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
                ret = handle_nxapi_error(command)
                if ret == 'FAILURE':
                    status['status'] = ret
                    status["log"] = response["error"]
                    return status
        except requests.exceptions.Timeout:
            print 'timeout occured while running', command
            status["status"] = 'FAILURE'
            status["log"] = "Timed Out"
            return status
            break
        except Exception as e:
            print e, ' while running ', command
            status['status'] = 'FAILURE'
            status["log"] = str(e)
            return status
            break
        payload.pop()
    status['status'] = 'SUCCESS'
    return status


def update_epld_image_single_switch(switch, image):
    url = build_nxapi_url(switch["ip"])
    scp_string = build_scp_string(image["image_server_username"], image["image_server_ip"], image["system_image"])
    ecp_string = build_scp_string(image["image_server_username"], image["image_server_ip"], image["epld_image"])
    system_image_name = image["system_image"].split(r'/')[-1]
    epld_image_name = image["epld_image"].split(r'/')[-1]
    myheaders = {'content-type': 'application/json-rpc'}
    commands = []
    commands.append(['terminal dont-ask', 7, 'set'])
    
    commands.append(['terminal password ' + image["image_server_password"], 7, ''])
    commands.append(['del bootflash:' + system_image_name + ' no-prompt', 70, ''])
    commands.append(['copy ' + scp_string + ' bootflash:' + system_image_name + ' vrf management', 300, 'scp'])
    commands.append(['no terminal password', 7, 'set'])
    
    commands.append(['terminal password ' + image["image_server_password"], 7, ''])
    commands.append(['del bootflash:' + epld_image_name + ' no-prompt', 70, ''])
    commands.append(['copy ' + ecp_string + ' bootflash:' + epld_image_name + ' vrf management', 300, 'scp'])
    commands.append(['no terminal password', 7, 'set'])
    
    commands.append(['boot nxos bootflash:'+system_image_name, 70, ''])
    commands.append(['copy running-config startup-config', 7, 'copy-config'])
    commands.append(['del ignite-config-bkp', 7, 'copy-config'])   
    commands.append(['copy running-config ignite-config-bkp', 7, 'copy-config']) 
    
    commands.append(['write erase', 70, ''])
    
    commands.append(['install all nxos bootflash:' + system_image_name, 500, 'system-install'])
    commands.append(['terminal dont-ask', 7, 'set'])
    commands.append(['install epld bootflash:' + epld_image_name + ' module all', 500, 'epld-install'])
	
	
    commands.append(['copy ignite-config-bkp startup-config', 7, 'copy-config'])
    payload = []
    payload_temp = []
    status = {"status":"","log":""}
    print url
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
                ret = handle_nxapi_error(command)
                if ret == 'FAILURE':
                    status["status"]=ret
                    status["log"]=response["error"]
                    return status['status']
                elif command[2]=='system-install':
                    print 'going to wait 300 seconds'
                    time.sleep(300)
        except requests.exceptions.Timeout:
            print 'timeout occured while running', command
            status["status"]='FAILURE'
            status["log"]="Timed Out"
            return status
        except Exception as e:
            print e, ' while running ', command
            status["status"]='FAILURE'
            status["log"]=str(e)
            return status
        payload.pop()
    status["status"]='SUCCESS'
    return status

