__author__ = 'sjaiswal'

"""
This module takes JSON file from POAP and converts it to
ANK understandble JSON format. Currently it takes the following format of

from,

{"core_list":[],"spine_list":[],"host_list":[],"leaf_list":[],"link_list":[]}

to,

{"directed":"false", "graph":[],"profiles":[],"links":[],"multigraph":False,"nodes":[]}

"""
import os
import sys
import time
import traceback
from datetime import datetime
import console_script
import argparse
from xml.etree.ElementTree import ElementTree
import random
import json
from pprint import pprint
import autonetkit.log as log

def parse_options(argument_string=None):
    """Parse user-provided options"""
    import argparse
    usage = "json_converter -f data.json"
    parser = argparse.ArgumentParser(description=usage)

    #input_group = parser.add_mutually_exclusive_group()
    parser.add_argument(
        '--file', '-f', default=None, help="Load POAP JSON topology from FILE")

    parser.add_argument(
        '--portchannel', '-pc', default=None, help = "Provide feature configuration file")

    if argument_string:
        arguments = parser.parse_args(argument_string.split())
    else:
        # from command line arguments
        arguments = parser.parse_args()

    return arguments

#generate random points for coordinates for locations of leafs and spines
def newpoint():
    from random import uniform
    return uniform(350,700), uniform(300, 500)

def create_args():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--file', '-f', default=None, help="Load POAP JSON topology from FILE")

    parser.add_argument(
        '--config', '-c', default=None, help = "Provide feature configuration file")

    parser.add_argument(
        '--monitor', '-m', action="store_true", default=False,
        help="Monitor input file for changes")
    parser.add_argument('--debug', action="store_true",
                        default=False, help="Debug mode")
    parser.add_argument('--quiet', action="store_true",
                        default=False, help="Quiet mode (only display warnings and errors)")
    parser.add_argument('--diff', action="store_true", default=False,
                        help="Diff DeviceModel")
    parser.add_argument('--no_vis', dest="visualise",
        action="store_false", default=True,
        help="Visualise output")
    parser.add_argument('--compile', action="store_true",
                        default=False, help="Compile")
    parser.add_argument(
        '--build', action="store_true", default=False, help="Build")
    parser.add_argument(
        '--render', action="store_true", default=False, help="Compile")
    parser.add_argument(
        '--validate', action="store_true", default=False, help="Validate")
    parser.add_argument('--deploy', action="store_true",
                        default=False, help="Deploy")
    parser.add_argument('--archive', action="store_true", default=False,
                        help="Archive ANM, DeviceModel, and IP allocations")
    parser.add_argument('--measure', action="store_true",
                        default=False, help="Measure")
    parser.add_argument(
        '--webserver', action="store_true", default=False, help="Webserver")
    parser.add_argument('--grid', type=int, help="Grid Size (n * n)")
    parser.add_argument(
        '--target', choices=['netkit', 'cisco'], default='cisco')
    parser.add_argument(
        '--vis_uuid', default=None, help="UUID for multi-user visualisation")

        # from command line arguments
    arguments = parser.parse_args()

    arguments.target = 'cisco'

    return arguments

class test:
    archive = False
    build = False
    compile = False
    debug = False
    deploy = False
    diff = False
    file = '/home/dev/temp.json'
    grid = None
    measure = False
    monitor = False
    quiet = False
    render = False
    stdin = False
    target = 'cisco'
    validate = True
    vis_uuid = None
    visualise = True
    webserver = False
    config = 'xyz'


def main(topo_file, cfg_file):
    import json

    dst_folder = None
    try:
        json_data=open(topo_file).read()
    except:
        log.error("json_converter.py...file open failed for topo_file")
        return dst_folder

    try:
        data = json.loads(json_data)
    except ValueError, e:
        #Error in JSON format. Check JSON file
        log.error("json_converter.py...Error in JSON format. Loading of topology json failed")
        return dst_folder

    #Create JSOn from POAP json
    ank_data = createAnkJsonData(data)

    if ank_data['nodes'] is None:
        log.error("json_converter.py...No nodes found in topology json.")
        return None

    try:
    #Add config info onto nodes.
        applyConfig(data, ank_data, cfg_file)
    except:
        log.error("json_converter.py...applyConfig failed")
        return dst_folder

    options = test()
    #options = create_args()
    options.debug = True
    #write ank_data to a file
    #we will write ank data in the same directory where topo_file resides.
    #so first we will extract the directory from that path

    try:
        pos = topo_file.rfind('/')
    except:
        pos = -1
    options.file = topo_file[:pos+1] + 'temp.json'

    try:
        with open(options.file, "w+") as fpc:
            fpc.write(json.dumps(ank_data))
    except:
        log.error("json_converter.py...Failed to create ank input json file.")
        return dst_folder

    try:
        dst_folder = console_script.main(options)
        return dst_folder
    except:
        log.error("json_converter.py...call to ank failed.")
        return dst_folder


def applyConfig(data, ank_data, cfg):

    if data.has_key('link_list'):
        configurePortChannel(data, ank_data)
        configureVirtualPortChannel(data, ank_data)
    ank_data = AddConfigInfo(ank_data, cfg)
    if ank_data is None:
        log.error("VPC id block is not correct")
        raise ValueError('Range not proper')

    '''
    By default ASN was set to 1. If BGP profile is applicable
    on the node then ASN may be different. We will be filling
    ASN info from BGP profile.
    '''
    ank_data = AddAsnInfo(ank_data, cfg)

def createAnkJsonData(data):
    #Prepare ank json format from poap json
    ank_data = {"directed":"false",
                          "graph":[],
                          "profiles":[],
                          "links":[],
                          "multigraph":"false",
                          "nodes":[]
                        }


    ank_data['profiles'] = []

    #add leaf nodes to nodes list
    if data.has_key('leaf_list'):
        for leafs in data['leaf_list']:
            node = {}
            ports = []
            node['asn'] = 1
            node['device_type'] = "router" #ANK picks it as router. Not sure why.
            node['devsubtype'] = "leaf" #this might be needed later to identify type of node
            if leafs.has_key('profile_id'):
                node['profile'] = leafs['profile_id']
            if leafs.has_key('name'):
                node['id']= leafs['name']
            else:
                node['id'] = "leaf" + str(random.randint(1000, 10000))

            points = (newpoint() for x in xrange(100))
            for x,y in points:
                node['x'] = x
                node['y'] = y
                break

            ank_data["nodes"].append(node)

    #Add spine nodes to node list
    if data.has_key('spine_list'):
        for spines in data['spine_list']:
            node = {}
            ports = []

            node['asn'] = 1
            node['device_type'] = "router"
            node['devsubtype'] = "spine" #this might be needed later to identify type of node
            if spines.has_key('profile_id'):
                node['profile'] = spines['profile_id']
            if spines.has_key('name'):
                node['id']= spines['name']
            else:
                node['id'] = "spine" + str(random.randint(1000, 10000))

            points = (newpoint() for x in xrange(100))
            for x,y in points:
                node['x'] = x
                node['y'] = y
                break

            ank_data["nodes"].append(node)

    #add core nodes to nodes list
    if data.has_key('core_list'):
        for core in data['core_list']:
            node = {}
            ports = []

            node['asn'] = 1 #Not sure why it should be 1 always for ANK. Need to change if required.
            node['device_type'] = "router" #ANK picks it as router. Not sure why.
            node['devsubtype'] = "core"
            if core.has_key('profile_id'):
                node['profile'] = core['profile_id']
            if core.has_key('name'):
                node['id']= core['name']
            else:
                node['id'] = "core" + str(random.randint(1000, 10000))

            points = (newpoint() for x in xrange(100))
            for x,y in points:
                node['x'] = x
                node['y'] = y
                break

            ank_data["nodes"].append(node)

    if ank_data['nodes'] is None:
        return ank_data

    for node in ank_data["nodes"]:
        node["ports"] = []

    #iterate thorugh the link_list and add them to links
    if data.has_key('link_list'):
        for links in data["link_list"]:
            for port_list1, port_list2 in zip(links["port_list_1"], links["port_list_2"]):
                if links['link_type']!= "VPC-MemberLink":
                    link = {}
                    link['src'] = links["switch_1"]
                    link['dst'] = links["switch_2"]
                    link["src_port"] = port_list1
                    link["dst_port"] = port_list2
                    ank_data["links"].append(link)


                #In POAP json file src and dst ports are missing in node port lists. If its not available, update them in node[ports] list
                for ank_nodes in ank_data["nodes"]:
                    if ank_nodes['id'] == link['src']:
                        matches = [prt for prt in ank_nodes['ports'] if prt['id'] == port_list1]
                        if not matches:
                            _p = {}
                            _p['id'] = port_list1
                            _p['category'] = "physical"
                            _p['subcategory'] = "physical"
                            _p['description'] = ""

                            ank_nodes['ports'].append(_p)
                            #print "not available, so update"
                    if ank_nodes['id'] == link['dst']:
                        matches = [prt for prt in ank_nodes['ports'] if prt['id'] == port_list2]
                        if not matches:
                            _p = {}
                            _p['id'] = port_list2
                            _p['category'] = "physical"
                            _p['subcategory'] = "physical"
                            _p['description'] = ""

                            ank_nodes['ports'].append(_p)

    #print "completed all configs"
    return ank_data

"""
Params:
        data - output of createAnkJsonData function
        ank_data - complete ANK formatted data with port channel info

Psuedo-code:


"""
def configurePortChannel(data, ank_data):
    #iterate through links and fill in port channel info

    for links in data["link_list"]:
        if links['link_type'] == "PC-2Link" or links['link_type'] == "VPC-MemberLink":
            port_list_1 = links["port_list_1"]
            port_list_2 = links["port_list_2"]
            rand_no = random.randint(1,10000)
            for node in ank_data['nodes']:
                if node['id'] == links["switch_1"]:
                    _p = {}
                    _p['id'] = links["switch_2"] + "_" + str(rand_no)
                    _p['category'] = "physical"
                    _p['subcategory'] = "port-channel"
                    _p['description'] = "port channel from"
                    _p['members'] = port_list_1
                    if links['link_type'] == "VPC-MemberLink":
                        _p['subcat_prot'] = "vpc-member"
                    node['ports'].append(_p)
                elif node['id'] == links["switch_2"]:
                    _p = {}
                    _p['id'] = links["switch_1"] + "_" + str(rand_no)
                    _p['category'] = "physical"
                    _p['subcategory'] = "port-channel"
                    _p['description'] = "port channel from"
                    _p['members'] = port_list_2
                    if links['link_type'] == "VPC-MemberLink":
                        _p['subcat_prot'] = "vpc-member"
                    node['ports'].append(_p)

def configureVirtualPortChannel(data, ank_data):
    #iterate through links and fill in port channel info

    for links in data["link_list"]:
        if links['link_type'] == "VPC-2Link":
            port_list_1 = links["port_list_1"]
            port_list_2 = links["port_list_2"]
            rand_no = random.randint(1,10000)
            for node in ank_data['nodes']:
                if node['id'] == links["switch_1"]:
                    _p = {}
                    _p['id'] = links["switch_2"] + "_" + str(rand_no)
                    _p['category'] = "physical"
                    _p['subcategory'] = "port-channel"
                    _p['subcat_prot'] = "vpc"
                    _p['description'] = "vpc"
                    _p['members'] = port_list_1
                    node['ports'].append(_p)
                elif node['id'] == links["switch_2"]:
                    _p = {}
                    _p['id'] = links["switch_1"] + "_" + str(rand_no)
                    _p['category'] = "physical"
                    _p['subcategory'] = "port-channel"
                    _p['subcat_prot'] = "vpc"
                    _p['description'] = "vpc"
                    _p['members'] = port_list_2
                    node['ports'].append(_p)

def AddConfigInfo(topo_data, cfg_data):
    import re
    config=open(cfg_data).read()
    config_data = json.loads(config)
    if config_data.has_key('device_profile') and config_data['device_profile'].has_key('profiles'):
        topo_data['profiles'] = config_data['device_profile']['profiles']

    #add mgmt_ip block
    if config_data['device_profile'].has_key('mgmt_block'):
        topo_data['mgmt_ip_block'] = config_data['device_profile']['mgmt_block']

    if config_data['device_profile'].has_key('vpcid_block'):
        topo_data['vpcid_block'] = config_data['device_profile']['vpcid_block']
        vpcids = topo_data['vpcid_block']
        vpc_re = "([0-9]+)(-)([0-9]+)"
        vpc_id_start = (re.search(vpc_re, vpcids)).group(1)
        vpc_id_end = (re.search(vpc_re, vpcids)).group(3)
        if int(vpc_id_end) < int(vpc_id_start):
            return None

    return topo_data

def AddAsnInfo(ank_data, options):

    for node in ank_data['nodes']:
        if node.has_key('profile'):
            profile = node['profile']
            for prof in ank_data['profiles']:
                if prof['id'] == profile and prof['configs'].has_key('bgp'):
                    node['asn'] = prof['configs']['bgp']['asn']

    return ank_data

def removeDuplicateLinks(list):
    new_list = []
    for elem in list:
        if elem not in new_list:
            new_list.append(elem)
    return new_list
def isPortsAvailable(pchannel, posts):
    for i in range (0, len(pchannel)):
        return list[i][1]==posts

def console_entry():
    args = parse_options()
    main(args)

if __name__ == "__main__":
    try:
        args = parse_options()
        main(args)
    except KeyboardInterrupt:
        pass


def run_ank(file, cfg, x, y):
    val = main(file, cfg)