import requests
from httplib2 import *
import os,sys
from urllib import *
import json

'''
cdp_data ={
    "system_id": "SAL1824UH92",
    "neighbor_list" : [
    {
        "local_port" : "Ethernet2/1",
        "remote_node" : "SPINE1",
        "remote_port" : "Ethernet1/1"
    },
    {
        "local_port" : "Ethernet2/2",
        "remote_node" : "LEAF2",
        "remote_port" : "Ethernet2/1"
    }
    ]
}
'''

cdp_data = {
    "system_id" : "PODA2LEAF1",
    "neighbor_list" : [
        {
            "local_port" : "e1/1",
            "remote_port" : "e1/1",
            "remote_node" : "PodA_2_spine1"
        }
    ]
}

class http_methods():
    h = Http()
    def __init__(self, url):
        self.url = url
    def Post_method(self, data):
        self.data = data
        resp, content = self.h.request(self.url, "POST", self.data, headers={'content-type': 'application/json'})
        #print ">>>>>", content
        #print "<<<<<", resp
        return resp, content

num = len(sys.argv)

if num == 1:
    server_ip = "127.0.0.1"
    port = "8000"
elif num == 2:
    server_ip = str(sys.argv[1])
    port = "8000"
elif num > 2:
    server_ip = str(sys.argv[1])
    port = str(sys.argv[2])

url = "http://" + server_ip + ":" + port + "/api/poap/"

cdp_json = json.dumps(cdp_data)
httpobj = http_methods(url)
resp, content = httpobj.Post_method(cdp_json)

print "Response =", resp
print "Content =", content
