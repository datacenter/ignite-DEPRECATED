import json
import sys
import os
import requests

BASE_DIR = os.path.join(os.getcwd(), "../..")
sys.path.append(os.path.join(BASE_DIR))

from ignite.conf import IGNITE_IP, IGNITE_PORT

def pull_config_from_switch(switch, image):
    print  switch
    status = {}
    try:
        URL = "http://" + IGNITE_IP + ":" + IGNITE_PORT
        LOGIN_URL = '/auth/login/'

        AUTH_HEADER = {"content_type": "application/json"}
        AUTH_DATA = {"username": "admin", "password": "admin"}

        auth = requests.post(url=URL+LOGIN_URL, data=AUTH_DATA, headers=AUTH_HEADER)
        token = json.loads(auth.text)['auth_token']
        headers_put = {"Authorization": token, "content-type": "application/json"}
        SW_URL = '/api/fabric/fabric/' + str(switch['fab_id']) + '/switch/' + str(switch['id']) + '/config/latest'
        sw_dat = json.dumps({"username": switch['user'], "password": switch['pwd']})
        url = URL+SW_URL
        response = requests.put(url, data=sw_dat, headers=headers_put)
        if response.status_code in [400, 404, 500]:
            status["status"]='FAILURE'
            status['log'] = response.text
        else:
            status["status"]='SUCCESS'
            status['log'] = 'success'
    except Exception as e:
        print e
        status['status'] = 'FAILURE'
        status['log'] = e
    return status
