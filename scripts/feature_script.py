import json
import os
import requests
import sys

BASE_DIR = os.path.join(os.getcwd(), "..")
sys.path.append(os.path.join(BASE_DIR))

from ignite.conf import IGNITE_IP, IGNITE_PORT


API_FEAT = "/api/feature/feature"
API_AUTH = "/auth/login/"
URL = "http://" + IGNITE_IP + ":" + IGNITE_PORT
URL_FEAT = URL + API_FEAT
URL_AUTH = URL + API_AUTH
AUTH_HEADER = {"content_type": "application/json"}
AUTH_DATA = {"username": "admin", "password": "admin"}


auth = requests.post(url=URL_AUTH, data=AUTH_DATA, headers=AUTH_HEADER)
token = json.loads(auth.text)["auth_token"]


features = [
    {
        "name": "bgp",
        "group": "default"
    },
    {
        "name": "snmp",
        "group": "default"
    },
    {
        "name": "ntp",
        "group": "default"
    }
]

fname_d = ["bgp.json", "snmp.json", "ntp.json"]


def upload_feature():

    for i in range(len(features)):
        data = json.dumps(features[i])
        headers_post = {'Authorization': token, 'content-type': 'application/json'}

        response = requests.post(URL_FEAT, data=data, headers=headers_post)
        url = URL_FEAT + "/" + str(json.loads(response.text)['id'])
        filepath = os.path.join(BASE_DIR, 'examples/features', fname_d[i])
        files = {"file": open(filepath, 'rb')}

        headers_put = {'Authorization': token}
        response = requests.put(url, headers=headers_put, files=files)
        files['file'].close()

upload_feature()
