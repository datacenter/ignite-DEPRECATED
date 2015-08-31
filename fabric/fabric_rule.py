#!/usr/bin/env python

import os
import json
from const import *
from switchdb import *
import re
import logging
from netaddr import *
from django.db import transaction

#Imports from user defined modules
from models import Fabric, FabricRuleDB
from collection.collection import generate_collection_value, generate_vpc_peer_dest
logger = logging.getLogger(__name__)


#Globals
switch_peer_map =   [] 
switch_type_map = {}
link_type_map = {}
vpc_detail_response = {} 
switch_fabric_if_list = []
leaf_list = []
spine_list = []
core_list = []


def get_instance_number(fabric_name, remote_node):
    regex = fabric_name + "(_)([1-9][0-9]*)(_)"
    instance_num = INVALID
    try:
        instance_num = (re.search(regex, remote_node)).group(2)
    except AttributeError:
        logger.error("Fabric Instance Number Not Found")
    return instance_num


def is_empty(item):
    if len(item) > 0:
        return False
    return True


#{"CFG_ID":INVALID,"FABRIC_ID":INVALID,"SWITCH_ID":"switch name"}
def build_match_response(switch_name, fabric_id, configuration_id, match_response):

    match_response["CFG_ID"] = configuration_id
    match_response["FABRIC_ID"] = fabric_id
    match_response["SWITCH_ID"] = switch_name


def log_match_info(match_response):

    logger.info("Fabric ID: " + str(match_response["FABRIC_ID"]))
    logger.info("Switch Name: "+ match_response["SWITCH_ID"])
    logger.info("Configuration Id: " + str(match_response["CFG_ID"]))


#delete all fabric rules with fabric_id == <fabric_id>
@transaction.atomic
def delete_fabric_rules(fabric_id):
    FabricRuleDB.objects.filter(fabric_id = fabric_id).delete()
    return True


#Write to Fabric DB
def write_to_FabricRuleDB(local_node, remote_node, local_port, remote_port, action, fabric):

    fabricRuleDB_obj                = FabricRuleDB()
    fabricRuleDB_obj.local_node     = local_node
    fabricRuleDB_obj.remote_node    = remote_node
    fabricRuleDB_obj.remote_port    = remote_port
    fabricRuleDB_obj.local_port     = local_port
    fabricRuleDB_obj.action         = action
    fabricRuleDB_obj.fabric         = fabric
    fabricRuleDB_obj.save()


#To build Fabric specific Rule DB
#Input
#1.fabric_name : Name of Fabric
#2.instances  : Number of Replicas for this Fabric
#3.fabric     : Fabric DB object
#4.switch_config_info : {{"switch_name":"Name","configuration_id":value},{"switch_name":"Name", "configuration_id":value},...}
#5.topology_info : Topology JSON File loaded into dictionary, please see topology_put.json sample file
#Output
#1.Fabric Specific Rule DB . Please see Fabric Model in models.py

@transaction.atomic
def generate_fabric_rules(fabric_name ,num_instance, fabric, switch_config_info, topology_info):

    switch_to_configuration_id = {}
    switch_set = set()
    core_switch_list = []
    core_switch_info = topology_info[CORE_LIST]
    link_list = topology_info[LINK_LIST]

    for switch_info in core_switch_info:
        core_switch_list.append(switch_info[SWITCH_NAME])

    for link in link_list:
       switch_set.add(link[SWITCH_1])
       switch_set.add(link[SWITCH_2])

    for item in switch_config_info:
        if item[SWITCH_NAME] not in switch_set:
            logger.error("Switch: " +  item[SWITCH_NAME] +" not a member of base topology")
            return False
        switch_to_configuration_id[item[SWITCH_NAME]] = item[CONFIGURATION_ID]

    for link in link_list:
        for inst in range(num_instance):
            inst_str = "_" + str(inst + 1) + "_"
            switch1 = fabric_name + inst_str + link[SWITCH_1]
            switch2 = fabric_name + inst_str + link[SWITCH_2]

            for index in range(len(link[PORTLIST_1])):
                try:
                    action = switch_to_configuration_id[link[SWITCH_1]]
                except KeyError:
                    action = INVALID
                    logger.error("No Configuration provided for switch: " + switch1 + " Adding Configuraion ID: INVALID")
                if switch1 not in core_switch_list:
                    write_to_FabricRuleDB(switch1, switch2, link[PORTLIST_1][index], link[PORTLIST_2][index], action, fabric)

                try:
                    action = switch_to_configuration_id[link[SWITCH_2]]
                except KeyError:
                    action = INVALID
                    logger.error("No Configuration provided for switch: " + switch2 + " Adding Configuraion ID: INVALID")
                if switch2 not in core_switch_list:
                    write_to_FabricRuleDB(switch2, switch1, link[PORTLIST_2][index], link[PORTLIST_1][index], action, fabric)

    logger.info("Write To Fabric Rule DB successfull")
    return True



#Function to parse topology JSON and buid following maps
#switch_tier_map : switch_name -> Tier
#switch_peer_map : switch_name - > [{peer_name:[[source port list][destination port list]]}, {peer_name:[[source port list][destination port list]]}]
def add_to_peer_map(peer_switch_name, localport_list, remoteport_list):

    peer_info = dict()
    peer_info[peer_switch_name] = [localport_list, remoteport_list]
    switch_peer_map.append(peer_info)


def build_fabric_map(fabric_name, topology_obj, local_node):

    have_fabric_ports = False
    topology_info = json.loads(topology_obj.topology_json)

    for switch in topology_info[CORE_LIST]:
        key = fabric_name + switch[SWITCH_NAME]
        core_list.append(key)
        switch_type_map[key] = switch[SWITCH_TYPE]
    for switch in topology_info[SPINE_LIST]:
        key = fabric_name + switch[SWITCH_NAME]
        spine_list.append(key)
        switch_type_map[key] = switch[SWITCH_TYPE]
    for switch in topology_info[LEAF_LIST]:
        key = fabric_name + switch[SWITCH_NAME]
        leaf_list.append(key)
        switch_type_map[key] = switch[SWITCH_TYPE]

    for link in topology_info[LINK_LIST]:
        have_fabric_ports = False
        switch1 = fabric_name + link[SWITCH_1]
        switch2 = fabric_name + link[SWITCH_2]
        if ((switch1 == local_node) or (switch2 == local_node)):
            if (((switch1 in leaf_list) and (switch2 in spine_list)) or\
                ((switch2 in leaf_list) and (switch1 in spine_list))):
                    have_fabric_ports = True 

            if switch1 == local_node:
                add_to_peer_map(switch2, link[PORTLIST_1],link[PORTLIST_2])
                link_type_map.update({switch2:link[LINK_TYPE]})
                if have_fabric_ports:
                    for port in link[PORTLIST_1]:
                        switch_fabric_if_list.append(port)
            else:
                add_to_peer_map(switch1, link[PORTLIST_2], link[PORTLIST_1])
                link_type_map.update({switch1:link[LINK_TYPE]})
                if have_fabric_ports:
                    for port in link[PORTLIST_2]:
                        switch_fabric_if_list.append(port)
                        

#To find the VPC peers of a leaf switch
#Input:
#1. leaf switch name
#2. cdp info.
#output: VPC_DETAIL_RESPONSE = {VPC_PEER_SWITCH:"",VPC_SWITCH_LOCALPORT:[]}
def build_vpc_detail(switch):

    vpc_peer_switches = []
    vpc_switch_localport = []
    peer_cdp_status = []
    peer_detail_list = switch_peer_map
    for peer_detail in  peer_detail_list:
        for peer,port_list in peer_detail.items():
            if  re.match(TOPOLOGY_LINK_TYPES[1], link_type_map[peer]):
                localport_list = port_list[0]
                vpc_detail_response[VPC_PEER_SWITCH] = peer
                vpc_detail_response[VPC_SWITCH_LOCALPORT] = localport_list
                break

    logger.debug("VPC Details- Local_Node "+ switch + " Peer_Switch: " + vpc_detail_response[VPC_PEER_SWITCH])


#To search Fabric Based Rule DB
#Input  : cdp neighbour info. cdp_neighbors
#output :
#match_response = \
#{"CFG_ID":INVALID,"FABRIC_ID":INVALID,"SWITCH_ID":"switch name"}
def match_fabric_rules(poap_info):

    #clean up the global DS on receive on new CDP info.
    global switch_peer_map
    switch_peer_map = []
    global switch_fabric_if_list
    switch_fabric_if_list = [] 
    global switch_type_map
    switch_type_map = {}
    global vpc_detail_response
    vpc_detail_response = dict(VPC_DETAIL_RESPONSE) 
    global leaf_list
    leaf_list = []
    global spine_list
    spine_list = []
    global core_list
    core_list = []
    global link_type_map
    link_type_map = {}

    cdp_neighbors = poap_info[NEIGHBOR_LIST]
    configuration_id = INVALID
    fabricRuleDB_obj= FabricRuleDB
    remote_node  = ""
    local_node = ""
    fabric_id = INVALID
    match_response = dict(FABRIC_MATCH_RESPONSE)

    if not is_empty(cdp_neighbors):
        for link in cdp_neighbors:
            remote_node = link[REMOTE_NODE]
            remote_port = link[REMOTE_PORT]
            local_port = link[LOCAL_PORT]
            logger.debug("Neighbour" + str(link))
            try:
                fabricRuleDB_obj = FabricRuleDB.objects.get(remote_node = remote_node, remote_port = remote_port, local_port = local_port)
                configuration_id = fabricRuleDB_obj.action
                fabric_id = fabricRuleDB_obj.fabric.id
                fabric_name = fabricRuleDB_obj.fabric.name
                local_node = fabricRuleDB_obj.local_node
                logger.debug("FabricRuleDB DB Match Success")
                break
            except FabricRuleDB.DoesNotExist:
                logger.error("FabricRuleDB DB Match Failed")

        if configuration_id != INVALID:
            topology_obj = fabricRuleDB_obj.fabric.topology
            instance_num = get_instance_number(fabric_name, local_node)
            fabric_name = fabric_name + "_" + instance_num + "_"
            build_fabric_map(fabric_name, topology_obj, local_node)
            build_match_response(local_node, fabric_id, configuration_id, match_response)
            log_match_info(match_response)
            try:
                build_vpc_detail(local_node)
            except KeyError,e:
                logger.error("Key:" + str(e) + " not found")
                return match_response

    #Let Global Rules take care of every thing
    return match_response


def generate_instance_value(param_name, fabric_id, switch_name):

    if  param_name == 'SWITCH_NAME':
        logger.debug("Parameter SWITCH_NAME: " + switch_name)
        return switch_name

    if  param_name == 'VPC_PEER_LINK_IF_NAMES':
        port_list = vpc_detail_response[VPC_SWITCH_LOCALPORT]
        if is_empty(port_list):
            logger.error("Parameter VPC_PEER_LINK_IF_NAMES is NOT Valid for switch: " + switch_name)
            return "[]"
        port_str = "[ \'" + '\',\''.join(port_list) + "\' ]"
        logger.debug("Parameter VPC_PEER_LINK_IF_NAMES: " + port_str)
        return port_str


    if  (param_name == 'VPC_PEER_DST' or param_name == 'VPC_PEER_SRC'):
        peer_switch = ""
        ip_str = "0.0.0.0" #Default Value
        peer_switch = vpc_detail_response[VPC_PEER_SWITCH]
        if peer_switch:
            logger.debug("Peer Switch = " + peer_switch)
            if param_name == 'VPC_PEER_DST':
                ip_addr = generate_vpc_peer_dest(fabric_id, switch_name, peer_switch)
            else:
                ip_addr = generate_vpc_peer_dest(fabric_id, peer_switch, switch_name)
            if ip_addr != None:
                ip_str = IPNetwork(ip_addr).ip.__str__()
                logger.debug("Parameter VPC_PEER_DST/VPC_PEER_SRC: " + ip_str)
        else:
            logger.error("Parameter VPC_PEER_DEST is NOT Valid for switch: " + switch_name)
        return ip_str

    if  param_name == 'HOST_INTERFACE':
        try:
            port_list = SWITCH_HOST_IF_MAP[switch_type_map[switch_name]]
            if is_empty(port_list):
                return "[]"
        except KeyError:
            logger.debug("Host Interfaces: No Host ports for Spine switch")
            return "[]"
        port_str = "[ \'" + '\',\''.join(port_list) + "\' ]"
        logger.debug("Host Interfaces: " + port_str )
        return port_str
            
             
    if  param_name == 'FABRIC_PORTS':
        port_list  = switch_fabric_if_list
        if port_list:
            port_str = "[ \'" + '\',\''.join(port_list) + "\' ]"
            logger.debug("Fabric Interface: " + port_str )
            return port_str
        logger.error("No Fabric Interfaces Found")
        return "[]"

