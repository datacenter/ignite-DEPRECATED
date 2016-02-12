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
import re
from utils.utils import string_to_ports

VPC_LINK_TYPE = 'VPC-Peer'
PC_LINK_TYPE = 'Port-Channel'
VPC_MEMBERLINK_TYPE = 'VPC-Member'
PC_GENERIC = 'V?PC-(([1-9][0-9]*)|(Member))Link'

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
    file = 'dictionary'
    dictionary = {}
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
    syntax = 'nx_os'

def main(topo_data, cfg_data, fab, syntax, fab_id, pool_dict):
    import json
    dst_folder = None
    config_passed = False
    data = topo_data
    if cfg_data is not None:
    	cfg_data = {"device_profile": cfg_data}
        #Above is done so that we don't need to make change to other functions
        config_passed = True
    #Create JSOn from POAP json
    ank_data = createAnkJsonData(data, cfg_data)
    if ank_data['nodes'] is None:
        log.debug("json_converter.py...Error received in createAnkJsonData.")
        return None

    try:
    #Add config info onto nodes.
        if config_passed == True:
            applyConfig(data, ank_data, cfg_data, fab, fab_id, pool_dict)
            log.debug("json_converter.py...applyConfig completed")
        else:
            log.debug("json_converter.py...no seperate config info supplied")
    except:
        log.error("json_converter.py...applyConfig failed")
        return dst_folder

    options = test()
    #options = create_args()
    options.debug = True
    options.syntax = syntax

    #Since input is coming from poap we can assume that it will
    #be a dictionary. Otherwise it will be a file.
    #options.file = 'temp.json'
    options.file = 'dictionary'
    options.dictionary = ank_data

    try:
        dst_folder = console_script.main(options)
        log.debug("json_converter.py...call to ank completed.")
        log.debug(str(dst_folder))
        return dst_folder
    except:
        log.error("json_converter.py...call to ank failed.")
        return dst_folder

def applyConfig(data, ank_data, cfg_data, fab, fab_id, pool_dict):

    ank_data = add_generic_config_info(ank_data, cfg_data, fab, fab_id, pool_dict)
    ank_data = configure_bgp(ank_data)
    ank_data = configure_vxlan(ank_data)
def createAnkJsonData(data, cfg):
    #Prepare ank json format from poap json
    ank_data = {"directed":"false",
                          "graph":[],
                          "profiles":[],
                          "links":[],
                          "multigraph":"false",
                          "nodes":[]
                        }


    ank_data['profiles'] = []
    switchid_to_name = {}

    if data.has_key('switches'):
        for switch in data['switches']:
            node = {}
            ports = []
            node['asn'] = 1
            node['device_type'] = "router" #ANK picks it as router. Not sure why.
            if switch['tier'] == 'Core':
                node_type = 'core' #this might be needed later to identify type of node
            elif switch['tier'] == 'Spine':
                node_type = 'spine'
            elif switch['tier'] == 'Leaf':
                node_type = 'leaf'
	    elif switch['tier'] == 'Border':
		node_type = 'border'
            if switch.has_key('feature_profile'):
                node['profile'] = switch['feature_profile']
            else:
                log.debug("feature_profile not specified for switch")
                return None

            #we are using 'name' as 'id' since that is used by ank in all the descriptions
            #while generating config.
            node['devsubtype'] = node_type
            if switch.has_key('name'):
                node['id']= switch['name']
            else:
                log.debug("Name not specified for switch")
                return None

            #we are using 'id' as name since we need to create config files with 'id'.
            if switch.has_key('id'):
                node['name']= switch['id']
                switchid_to_name[switch['id']] = switch['name']
            else:
                log.debug("id not specified for switch")
                return None

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

    #generate_pc_cfg = False
    #if (cfg['device_profile'].has_key('pc_enabled') and
    #    cfg['device_profile']['pc_enabled'] == True):
    #    generate_pc_cfg = True

    #iterate thorugh the link_list and add them to links
    if data.has_key('links'):
        for links in data["links"]:
            links['src_ports'] = string_to_ports(links['src_ports'])
            links['dst_ports'] = string_to_ports(links['dst_ports'])
            #process PC seperately
            #if ((generate_pc_config == True) and
            if  ((re.search(VPC_LINK_TYPE , links['link_type'])) or
                (re.search(PC_LINK_TYPE , links['link_type'])) or
                (re.search(VPC_MEMBERLINK_TYPE , links['link_type']))):
                configure_PC_VPC(links, ank_data, switchid_to_name)
                continue

            src_node_type = dest_node_type = None
            for ank_nodes in ank_data["nodes"]:
                if ank_nodes['id'] == switchid_to_name[links['src_switch']]:
                    src_node = ank_nodes
                    src_node_type = ank_nodes['devsubtype']
                if ank_nodes['id'] == switchid_to_name[links['dst_switch']]:
                    dest_node = ank_nodes
                    dest_node_type = ank_nodes['devsubtype']
                if src_node_type is not None and dest_node_type is not None:
                    break

            for port_list1, port_list2 in zip(links["src_ports"], links["dst_ports"]):
                link = {}
                link["src"] = switchid_to_name[links['src_switch']]
                link["dst"] = switchid_to_name[links['dst_switch']]
                link["src_port"] = port_list1
                link["dst_port"] = port_list2
                link["link_type"] = links['link_type']
                #SHARAD: for not generating ip address
                #link["link_type"] = 'is_not_l3'
                ank_data["links"].append(link)

                #In POAP json file src and dst ports are missing in node port lists. If its not available, update them in node[ports] list

                _p = {}
                _p['id'] = port_list1
                _p['category'] = "physical"
                _p['subcategory'] = "physical"
                _p['description'] = ""
                _p['connected_to'] = dest_node_type
                #_p['ipv4_address'] = "11.0.0.8"
                #_p['ipv4_prefixlen'] = 30

                src_node['ports'].append(_p)

                _p = {}
                _p['id'] = port_list2
                _p['category'] = "physical"
                _p['subcategory'] = "physical"
                _p['description'] = ""
                _p['connected_to'] = src_node_type
                #_p['ipv4_address'] = "11.0.0.9"
                #_p['ipv4_prefixlen'] = 30
                dest_node['ports'].append(_p)

    #print "completed all configs"
    return ank_data

"""
Params:
        data - output of createAnkJsonData function
        ank_data - complete ANK formatted data with port channel info

Psuedo-code:


"""
def configurePC_Link(links, node_src, node_dest, switchid_to_name):
    rand_no = random.randint(1,4090)
    src_ports = links["src_ports"]
    dst_ports = links["dst_ports"]
    _p_src = {}
    _p_src['id'] = switchid_to_name[links['dst_switch']] + "_" + str(rand_no)
    _p_src['category'] = "physical"
    _p_src['subcategory'] = "port-channel"
    _p_src['description'] = "port channel from"
    _p_src['connected_to'] = node_dest['devsubtype']
    _p_src['members'] = src_ports

    node_src['ports'].append(_p_src)

    _p_dst = {}
    _p_dst['id'] = switchid_to_name[links['src_switch']] + "_" + str(rand_no)
    _p_dst['category'] = "physical"
    _p_dst['subcategory'] = "port-channel"
    _p_dst['description'] = "port channel from"
    _p_dst['connected_to'] = node_src['devsubtype']
    _p_dst['members'] = dst_ports

    node_dest['ports'].append(_p_dst)

    return (_p_src, _p_dst)

def configureVPC_Link(links, node_src, node_dest, switchid_to_name):
    (_p_src, _p_dst) = configurePC_Link(links, node_src, node_dest, switchid_to_name)
    ##add VPC peer specific info
    _p_src['subcat_prot'] = 'vpc'
    _p_dst['subcat_prot'] = 'vpc'
    node_dest['vpc_peer'] = node_src['id']
    node_src['vpc_peer'] = node_dest['id']

    return (_p_src, _p_dst)

def configureVPC_Member_Link(links, node_src, node_dest, switchid_to_name):
    (_p_src, _p_dst) = configurePC_Link(links, node_src, node_dest, switchid_to_name)
    ##add VPC member specific info
    _p_src['subcat_prot'] = 'vpc-member'
    _p_dst['subcat_prot'] = 'vpc-member'

    return (_p_src, _p_dst)

def configure_PC_VPC(links, ank_data, switchid_to_name):
    node_src = node_dest = None

    for node in ank_data['nodes']:
        if node['id'] == switchid_to_name[links['src_switch']]:
            node_src = node
        if node['id'] == switchid_to_name[links['dst_switch']]:
            node_dest = node
        if node_src is not None and node_dest is not None:
            break

    if re.search(VPC_LINK_TYPE, links['link_type']):
        (_p_src, _p_dst) = configureVPC_Link(links, node_src, node_dest, switchid_to_name)
    elif re.search(VPC_MEMBERLINK_TYPE, links['link_type']):
        (_p_src, _p_dst) = configureVPC_Member_Link(links, node_src, node_dest, switchid_to_name)
    elif re.search(PC_LINK_TYPE, links['link_type']):
        (_p_src, _p_dst) = configurePC_Link(links, node_src, node_dest, switchid_to_name)

    for port_list1, port_list2 in zip(links["src_ports"], links["dst_ports"]):
        #First we will add ports and then links

        #ADDING PORTS
        _p = {}
        _p['id'] = port_list1
        _p['category'] = "physical"
        _p['subcategory'] = "physical"
        _p['description'] = ""
        _p['connected_to'] = node_dest['devsubtype']

        node_src['ports'].append(_p)

        _p = {}
        _p['id'] = port_list2
        _p['category'] = "physical"
        _p['subcategory'] = "physical"
        _p['description'] = ""
        _p['connected_to'] = node_src['devsubtype']

        node_dest['ports'].append(_p)


        #ADDING LINKS
        #We will not be configuring l3 on member links of l3 PC so we need a way to not add them to l3
        #We will use link_type for that. Similar holds for l2 PC.

        #node_dest['devsubtype'] != node_src['devsubtype'] means the link is
        #not bw 2 leafs so this will be a layer 3 PC therefore we will treat
        #it's member links as not l3 links. Otherwise it will be a layer 2 PC
        # and we will treat it's member links as not l2 links
        if node_dest['devsubtype'] != node_src['devsubtype']:
            link = {}
            link["src"] = switchid_to_name[links['src_switch']]
            link["dst"] = switchid_to_name[links['dst_switch']]
            link["src_port"] = port_list1
            link["dst_port"] = port_list2
            link["link_type"] = 'is_not_l3'
            ank_data["links"].append(link)
        else:
            link = {}
            link["src"] = switchid_to_name[links['src_switch']]
            link["dst"] = switchid_to_name[links['dst_switch']]
            link["src_port"] = port_list1
            link["dst_port"] = port_list2
            link["link_type"] = 'is_not_l2'
            ank_data["links"].append(link)

    #node_dest['devsubtype'] != node_src['devsubtype'] means the link is
    #not bw 2 leafs so this will be a layer 3 PC therefore we will treat
    #it as l3 links. Otherwise it will be a layer 2 PC
    # and we will treat it as not l3 links
    if node_dest['devsubtype'] != node_src['devsubtype']:
        link = {}
        link["src"] = switchid_to_name[links['src_switch']]
        link["dst"] = switchid_to_name[links['dst_switch']]
        link["src_port"] = _p_src['id']
        link["dst_port"] = _p_dst['id']
        link["link_type"] = links["link_type"]
        ank_data["links"].append(link)
    else:
        link = {}
        link["src"] = switchid_to_name[links['src_switch']]
        link["dst"] = switchid_to_name[links['dst_switch']]
        link["src_port"] = _p_src['id']
        link["dst_port"] = _p_dst['id']
        link["link_type"] = 'is_not_l3'
        ank_data["links"].append(link)

def add_generic_config_info(topo_data, config_data, fab, fab_id, pool_dict):
    import re
    mgmt_block_specified = False
    if (config_data['device_profile'].has_key('profiles') and
        config_data['device_profile']['profiles'] is not None):
        topo_data['profiles'] = config_data['device_profile']['profiles']
    if (config_data['device_profile'].has_key('fabric_profile') and
        config_data['device_profile']['fabric_profile'].has_key('configs')):
        configs = config_data['device_profile']['fabric_profile']['configs']
        if configs.has_key('global_cfg'):
            global_cfg = configs['global_cfg']

            if global_cfg.has_key('pc_only'):
                topo_data['pc_only'] = global_cfg['pc_only']

	    if (global_cfg.has_key('igp_enabled') and
                global_cfg['igp_enabled'] == True):
                topo_data['igp'] = 'ospf'

            if (global_cfg.has_key('bgp_enabled') and
        	global_cfg['bgp_enabled'] is not None):
        	topo_data['bgp_enabled'] = global_cfg['bgp_enabled']

            if (global_cfg.has_key('enable_routing') and
        	global_cfg['enable_routing'] is not None):
        	topo_data['enable_routing'] = global_cfg['enable_routing']

    	    if (global_cfg.has_key('infra_block') and
        	global_cfg['infra_block'] is not None):
       	 	topo_data['infra_block'] = global_cfg['infra_block']

    	    if (global_cfg.has_key('loopback_block') and
	        global_cfg['loopback_block'] is not None):
        	topo_data['loopback_block'] = global_cfg['loopback_block']

	    #add mgmt_ip block
    	    if (global_cfg.has_key('mgmt_block') and
	        global_cfg['mgmt_block'] is not None):
        	topo_data['mgmt_ip_block'] = global_cfg['mgmt_block']
		mgmt_block_specified = True

        if (configs.has_key('vxlan') and 
            configs['vxlan'].has_key('vxlan_global_config')):
            config_vxlan = configs['vxlan']['vxlan_global_config']
            if config_vxlan is not None: 
                topo_data['vxlan_global_config'] = config_vxlan
    
    if pool_dict is not None:
        topo_data['ignite'] =  pool_dict
        if 'mgmt_pool_id' in pool_dict and pool_dict['mgmt_pool_id'] is not None:
                mgmt_block_specified = True

    if mgmt_block_specified == False:
       topo_data['mgmt_ip_block'] = "192.168.0.0/24"

    if (config_data['device_profile'].has_key('vpcid_block') and
        config_data['device_profile']['vpcid_block'] is not None):
        topo_data['vpcid_block'] = config_data['device_profile']['vpcid_block']
        vpcids = topo_data['vpcid_block']
        vpc_re = "([0-9]+)(-)([0-9]+)"
        vpc_id_start = (re.search(vpc_re, vpcids)).group(1)
        vpc_id_end = (re.search(vpc_re, vpcids)).group(3)

        if int(vpc_id_end) < int(vpc_id_start):
            raise ValueError('Range not proper')

    return topo_data

def configure_bgp(ank_data):

    for node in ank_data['nodes']:
        if node.has_key('profile') and node['profile'] is not None:
            profile = node['profile']
            for prof in ank_data['profiles']:
                if prof['id'] == profile and prof['configs'].has_key('bgp'):
                    node['asn'] = prof['configs']['bgp']['asn']
                    if 'route_reflector' in prof['configs']['bgp']:
                        node['route_reflector'] = prof['configs']['bgp']['route_reflector']
                    elif node['devsubtype'] == 'spine':
                        node['route_reflector'] = True

    return ank_data

def configure_vxlan(ank_data):

    l3_vni_info = {}
    l2_vni_info = {}
    vxlan_global_data ={}

    if ank_data.has_key('vxlan_global_config'):
        if 'tenant_info' in ank_data['vxlan_global_config']:
            for tenant in ank_data['vxlan_global_config']['tenant_info']:
                l3_vni_id = None
                control_vlan = None
                vrf_context = None
                temp_l3_vni_info = []
                if 'l3_vni' in tenant:
                    l3_vni_id = tenant['l3_vni']

                if 'control_vlan' in tenant:
                    control_vlan = tenant['control_vlan']

                if 'vrf_context' in tenant:
                    vrf_context = tenant['vrf_context']

                temp_l3_vni_info = [l3_vni_id, control_vlan, vrf_context]
                if l3_vni_id is not None:
                    l3_vni_info[tenant['id']] = temp_l3_vni_info

                if 'l2_vni_list' in tenant:
                    for l2_vni in tenant['l2_vni_list']:
                        anycast_gateway_address = None
                        vlan = None
                        mcast_group = None
                        l2_vni_id = None
                        temp_l2_vni_info = []
                        if 'vni' in l2_vni:
                            l2_vni_id = l2_vni['vni']

                        if 'anycast_gateway' in l2_vni:
                            anycast_gateway_address = l2_vni['anycast_gateway']

                        if 'vlan' in l2_vni:
                            vlan = l2_vni['vlan']

                        if 'mcast_group' in l2_vni:
                            mcast_group = l2_vni['mcast_group']

                        temp_l2_vni_info = [anycast_gateway_address, vlan, mcast_group, l3_vni_id]

                        if l2_vni_id is not None:
                            l2_vni_info[l2_vni_id] = temp_l2_vni_info

        vxlan_global_data['l2_vni_info'] = l2_vni_info
        vxlan_global_data['l3_vni_info'] = l3_vni_info
        if 'tenant_info' in ank_data['vxlan_global_config']:
            ank_data['vxlan_global_config']['vni_info'] = vxlan_global_data
        for node in ank_data['nodes']:
            if node.has_key('profile') and node['profile'] is not None:
                profile = node['profile']
                for prof in ank_data['profiles']:
                    if prof['id'] == profile:
                        if prof['configs'].has_key('vxlan'):
                            vxlan_cfg = prof['configs']['vxlan']
                            if (vxlan_cfg.has_key('vxlan_vni_configured') and
                                vxlan_cfg['vxlan_vni_configured'] is not None):
                                node['vxlan_vni_configured'] = vxlan_cfg['vxlan_vni_configured']
                        break

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
