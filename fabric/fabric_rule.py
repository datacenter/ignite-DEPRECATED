
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
from fabric_profile.models import FabricProfile
from pool.pool import generate_pool_value, generate_vpc_peer_dest
from pool.models import Pool
from server_configuration import PROJECT_DIR, REPO
#from autonetkit.start_ank import run_ank
logger = logging.getLogger(__name__)

BASE_PATH = os.getcwd() + PROJECT_DIR + REPO
ANK_PROFILE_FILE = ".ank.prof"
ANK_TOPOLOGY_FILE = ".ank.topo"
ANK_CONFIG_FILE = ".ank.cfg"


#Globals
switch_peer_map =   [] 
switch_type_map = {}
link_type_map = {}
vpc_detail_response = {} 
switch_fabric_if_list = []
leaf_list = []
spine_list = []
core_list = []

def clear_globals():
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

def purge_domainname(switch_name):
	return switch_name.split(".",1)[0]

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
def build_match_response(switch_name, fabric_id, configuration_id, replica_num, match_type, match_response):

    match_response["CFG_ID"] = configuration_id
    match_response["FABRIC_ID"] = fabric_id
    match_response["SWITCH_ID"] = switch_name
    match_response["REPLICA_NUM"] = replica_num
    match_response["MATCH_TYPE"] = match_type


def log_match_info(match_response):

    logger.info("Fabric ID: " + str(match_response["FABRIC_ID"]))
    logger.info("Switch Name: "+ match_response["SWITCH_ID"])
    logger.info("Configuration Id: " + str(match_response["CFG_ID"]))
    logger.info("Discoveryrule Id: " + str(match_response["DISCOVERYRULE_ID"]))
    logger.info("Match Type: " + str(match_response["MATCH_TYPE"]))
    logger.info("Replica Num: " + str(match_response["REPLICA_NUM"]))


#delete all fabric rules with fabric_id == <fabric_id>
@transaction.atomic
def delete_fabric_rules(fabric_id):
    FabricRuleDB.objects.filter(fabric_id = fabric_id).delete()
    return True


#Write to Fabric DB
def write_to_FabricRuleDB(local_node, remote_node, local_port, remote_port, action, fabric, replica_num):

    fabricRuleDB_obj                = FabricRuleDB()
    fabricRuleDB_obj.local_node     = local_node
    fabricRuleDB_obj.remote_node    = remote_node
    fabricRuleDB_obj.remote_port    = remote_port
    fabricRuleDB_obj.local_port     = local_port
    fabricRuleDB_obj.action         = action
    fabricRuleDB_obj.fabric         = fabric
    fabricRuleDB_obj.replica_num    = replica_num
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
def generate_fabric_rules(fabric_name ,num_instance, fabric, switch_to_configuration_id, topology_info):

    switch_set = set()
    core_switch_list = []
    core_switch_info = topology_info[CORE_LIST]
    link_list = topology_info[LINK_LIST]

    for switch_info in core_switch_info:
        core_switch_list.append(switch_info[SWITCH_NAME])

    for link in link_list:
       switch_set.add(link[SWITCH_1])
       switch_set.add(link[SWITCH_2])

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
                    write_to_FabricRuleDB(switch1, switch2, link[PORTLIST_1][index], link[PORTLIST_2][index], action, fabric, inst+1)

                try:
                    action = switch_to_configuration_id[link[SWITCH_2]]
                except KeyError:
                    action = INVALID
                    logger.error("No Configuration provided for switch: " + switch2 + " Adding Configuraion ID: INVALID")
                if switch2 not in core_switch_list:
                    write_to_FabricRuleDB(switch2, switch1, link[PORTLIST_2][index], link[PORTLIST_1][index], action, fabric, inst+1)

    logger.info("Write To Fabric Rule DB successfull")
    return True



#Function to parse topology JSON and buid following maps
#switch_tier_map : switch_name -> Tier
#switch_peer_map : switch_name - > [{peer_name:[[source port list][destination port list]]}, {peer_name:[[source port list][destination port list]]}]
def add_to_peer_map(peer_switch_name, localport_list, remoteport_list):

    peer_info = dict()
    peer_info[peer_switch_name] = [localport_list, remoteport_list]
    switch_peer_map.append(peer_info)
    peer_map_str = json.dumps(switch_peer_map)
    logger.debug("Peer map for switch %s:" %(peer_map_str))

def build_fabric_map(fabric_name, topology_obj, local_node):

    have_fabric_ports = False
    topology_info = json.loads(topology_obj.topology_json)

    logger.debug("Building peer map for switch: %s" %(local_node))

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
    clear_globals()
    global switch_peer_map
    global switch_fabric_if_list
    global switch_type_map
    global vpc_detail_response
    global leaf_list
    global spine_list
    global core_list
    global link_type_map

    cdp_neighbors = poap_info[NEIGHBOR_LIST]
    configuration_id = INVALID
    fabricRuleDB_obj= FabricRuleDB
    remote_node  = ""
    local_node = ""
    replica_num = INVALID
    fabric_id = INVALID
    match_response = dict(FABRIC_MATCH_RESPONSE)

    if not is_empty(cdp_neighbors):
        for link in cdp_neighbors:
            remote_node = purge_domainname(link[REMOTE_NODE])
            remote_port = link[REMOTE_PORT]
            local_port = link[LOCAL_PORT]
            logger.debug("Neighbour" + str(link))
            try:
                fabricRuleDB_obj = FabricRuleDB.objects.get(remote_node = remote_node, remote_port = remote_port, local_port = local_port)
                configuration_id = fabricRuleDB_obj.action
                fabric_id = fabricRuleDB_obj.fabric.id
                fabric_name = fabricRuleDB_obj.fabric.name
                local_node = fabricRuleDB_obj.local_node
                replica_num = fabricRuleDB_obj.replica_num
                logger.debug("FabricRuleDB DB Match Success")
                break
            except FabricRuleDB.DoesNotExist:
                logger.error("FabricRuleDB DB Match Failed")

        if configuration_id != INVALID:
            topology_obj = fabricRuleDB_obj.fabric.topology
            instance_num = get_instance_number(fabric_name, local_node)
            fabric_name = fabric_name + "_" + instance_num + "_"
            build_fabric_map(fabric_name, topology_obj, local_node)
            build_match_response(local_node, fabric_id, configuration_id, replica_num, MATCH_TYPE_NEIGHBOUR, match_response)
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

    if  param_name == 'HOST_PORTS':
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
            
             
    if  param_name == 'TRUNK_PORTS':
        port_list  = switch_fabric_if_list
        if port_list:
            port_str = "[ \'" + '\',\''.join(port_list) + "\' ]"
            logger.debug("Fabric Interface: " + port_str )
            return port_str
        logger.error("No Fabric Interfaces Found")
        return "[]"



#-------------Generate All configs for Fabric-----------

def generate_config(fabric_obj):
    
    from views import getConfig_id, getSwitch_list
    from configuration.config import build_file
    from ignite.ignite import insert_deployed_fabric_stats, sanitize_repo

    global switch_peer_map
    global switch_fabric_if_list
    global switch_type_map
    global vpc_detail_response
    global leaf_list
    global spine_list
    global core_list
    global link_type_map

    if fabric_obj == INVALID:
        logger.debug("Fabric not found for fabric-id %s" %fabric_id)
        return INVALID

    fabric_id = fabric_obj.id
    fabric_name = fabric_obj.name
    instance = fabric_obj.instance
    config_details = json.loads(fabric_obj.config_json)

    topology_obj = fabric_obj.topology
    topology_json = json.loads(topology_obj.topology_json)

    leaf_set = getSwitch_list(topology_json, LEAF_LIST)
    spine_set = getSwitch_list(topology_json, SPINE_LIST)    

    match_response = dict(FABRIC_MATCH_RESPONSE)
    file_name = ""

    switch_to_config_id = getConfig_id(config_details, spine_set, leaf_set)


    for inst in range(1, instance+1):
        for switch_name, cfg_id in switch_to_config_id.iteritems():
            switch_name = "%s_%s_%s" %(fabric_name, inst, switch_name)
            
            build_match_response(switch_name, fabric_id, cfg_id, inst, "", match_response) 
    
            clear_globals()
            fabric_name_with_replica = fabric_name + "_" + str(inst) + "_" 
            build_fabric_map(fabric_name_with_replica, topology_obj, switch_name)
            try:
                build_vpc_detail(switch_name)
            except KeyError,e:
                logger.error("Key:" + str(e) + " not found")

            file_name = build_file(cfg_id, fabric_id ,switch_name, build_type = BUILD_OFF, build_new_config = True) 

            if(file_name):
                logger.debug("Generated config for switch %s" %(switch_name))
            else:
                logger.debug("Failed to generate config for switch %s" %(switch_name))
            
            insert_deployed_fabric_stats(match_response, "", file_name, True)
            
            #file_path = BASE_PATH + file_name 
            #sanitize_repo(file_path)

    return True

#-------------Profile handling for fabric----------------


def get_profile_name(profile_id):
    
    try:
        profile_obj = FabricProfile.objects.get(id=profile_id)
    except:
        logger.error("Failed to fetch profile with id %s" %profile_id)
        return profile_id

    return profile_obj.name


def build_fabric_profiles(fabric_obj):
    
    logger.debug("Starting Profile build")    
    from configuration.config import build_file
    
    fh = ""
    profiles_created = []
    ank = dict(ANK)
    switch_to_profile_map = []
    fabric_name = fabric_obj.name
    fabric_id = fabric_obj.id 
    switch_profile_info = json.loads(fabric_obj.profiles)

    if is_empty(switch_profile_info):
        logger.debug("No fabric profiles provided for fabric: %s" %(fabric_name))
        return True
 
    instance = fabric_obj.instance
    topology_info = json.loads(fabric_obj.topology.topology_json)

    ank_profile_file = BASE_PATH + ANK_PROFILE_FILE
    ank_config_file = BASE_PATH + ANK_CONFIG_FILE
    ank_topo_file = BASE_PATH + ANK_TOPOLOGY_FILE
	
    leaf_profile_id = switch_profile_info[LEAF_PROFILE]
    leaf_profile_name = get_profile_name(switch_profile_info[LEAF_PROFILE])
    spine_profile_id = switch_profile_info[SPINE_PROFILE]
    spine_profile_name = get_profile_name(switch_profile_info[SPINE_PROFILE])
    spine_switch_info = topology_info[SPINE_LIST]
    leaf_switch_info = topology_info[LEAF_LIST]
		
    for sw in topology_info[SPINE_LIST]:
        sw[PROFILE_ID] = spine_profile_name
        profile_id = spine_profile_id
        for item in switch_profile_info[SWITCH_PROFILE]:
            if item[SWITCH_NAME] == sw[SWITCH_NAME]:
                sw[PROFILE_ID] = get_profile_name(item[PROFILE_ID])    
                profile_id = item[PROFILE_ID]
        switch_to_profile_map.append({SWITCH_NAME:sw[SWITCH_NAME], PROFILE_ID:profile_id})

    for sw in topology_info[LEAF_LIST]:
        sw[PROFILE_ID] = leaf_profile_name
        profile_id = leaf_profile_id
        for item in switch_profile_info[SWITCH_PROFILE]:
            if item[SWITCH_NAME] == sw[SWITCH_NAME]:
                sw[PROFILE_ID] = get_profile_name(item[PROFILE_ID])    
                profile_id = item[PROFILE_ID]
        switch_to_profile_map.append({SWITCH_NAME:sw[SWITCH_NAME], PROFILE_ID:profile_id})
        
    profile = []
    for sw in switch_to_profile_map:
        profile_id = sw[PROFILE_ID]
        if profile_id == INVALID:
            logger.debug("Invalid profile id for switch %s" %sw[SWITCH_NAME])
            continue

        profile_name = get_profile_name(profile_id) 

        with open(ank_config_file, "w") as fh:
            fh.write("{")
        
        if profile_id not in profiles_created:
                build_file(profile_id, fabric_id ,sw[SWITCH_NAME], ank_config_file, build_method = BUILD_PROFILE, build_type = BUILD_OFF ,build_new_config = True)

                with open(ank_config_file, "a") as fh:
                    fh.write("}")
                with open(ank_config_file, "r") as fh:
                    configs = json.loads(fh.read())

                temp = dict({CONFIGS:configs, ID:profile_name})
                profile.append(temp)
        profiles_created.append(profile_id)
    
    if is_empty(profile):
        logger.debug("No Profiles provided for fabric %s" %fabric_name)
        return True
 
    temp = dict({PROFILES:profile})
    ank[DEVICE_PROFILE].update(temp)

    with open(ank_profile_file, "w") as fh:
        fh.write(json.dumps(ank))

    with open(ank_topo_file, 'w') as fh:
        fh.write(json.dumps(topology_info))
    
    logger.debug("Completed Profile build")    

    logger.debug("Call to ANK")
    for instance_num in range(1, instance + 1):
        fabric_instance = fabric_name + "_" + str(instance_num)
        try: 
            #run_ank(ank_topo_file, ank_profile_file, fabric_instance, BASE_PATH)
            logger.debug("Success : call to ANK for %s" %(fabric_instance))
        except:
            logger.debug("Failed : call to ANK for %s" %(fabric_instance))
            pass

    return True    
