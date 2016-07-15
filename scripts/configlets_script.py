import json
import os
import requests
import sys

BASE_DIR = os.path.join(os.getcwd(), "..")
sys.path.append(os.path.join(BASE_DIR))

from ignite.conf import IGNITE_IP, IGNITE_PORT


API_CONF = "/api/config/configletindex"
API_AUTH = "/auth/login/"
URL = "http://" + IGNITE_IP + ":" + IGNITE_PORT
URL_CONF = URL + API_CONF
URL_AUTH = URL + API_AUTH
AUTH_HEADER = {"content_type": "application/json"}
AUTH_DATA = {"username": "admin", "password": "admin"}


auth = requests.post(url=URL_AUTH, data=AUTH_DATA, headers=AUTH_HEADER)
token = json.loads(auth.text)["auth_token"]


configlets = [
    {
        "name": "adminuser",
        "group": "default",
        "type" : "configlet"
    },
    {
        "name": "hostname",
        "group": "default",
        "type" : "configlet"
    },
    {
        "name": "mgmt",
        "group": "default",
        "type" : "configlet"
    },
    {
        "name": "xmpp",
        "group": "default",
        "type" : "configlet"
    }
]

fname_d = ["adminuser.txt", "hostname.txt", "mgmt.txt", "xmpp.txt"]


def upload_configlets():

    for i in range(len(configlets)):
        data = json.dumps(configlets[i])
        headers_post = {'Authorization': token, 'content-type': 'application/json'}

        response = requests.post(URL_CONF, data=data, headers=headers_post)
        url = URL_CONF + "/" + str(json.loads(response.text)['configletindex_id'])+"/True"
        filepath = os.path.join(BASE_DIR, 'examples/configlets', fname_d[i])
        files = {"file": open(filepath, 'rb')}

        headers_put = {'Authorization': token}
        response = requests.put(url, headers=headers_put, files=files)
        files['file'].close()

upload_configlets()
