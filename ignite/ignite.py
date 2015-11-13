from configuration.config import build_config
from discoveryrule.discoveryrule import match_discovery_rules 
from fabric.const import INVALID
from fabric.fabric_rule import match_fabric_rules 
from pool.pool import generate_pool_value
import os
from fabric.models import DeployedFabricStats, FabricRuleDB, Fabric, Topology
from configuration.models import Configuration
from fabric.const import *
import json
import re
from fabric.image_profile import image_objects

from server_configuration import VMUSERNAME, VMPASSWORD, PROJECT_DIR, REPO, DEFAULT_SWITCH_IMAGE_NAME
REPO_PATH = os.getcwd() + PROJECT_DIR + REPO
 
import logging
logger = logging.getLogger(__name__)


def swtType(switch, topology, fab_name, replica_num):
    for sw in topology['spine_list']:
        switchName = fab_name+'_'+str(replica_num)+'_'+sw['name']
        if str(switch) == switchName:
            return SPINE_SWITCH_TYPE
    for sw in topology['leaf_list']:
        switchName = fab_name+'_'+str(replica_num)+'_'+sw['name']
        if str(switch) == switchName:
            return LEAF_SWITCH_TYPE
    return INVALID

def fillResult(result,file_name,image_name,imageserver_ip,image_username,image_password,access_protocol):
    result["status"] = True
    result["imagename"] = image_name
    result["imageserver"] = imageserver_ip
    result["image_username"] = image_username
    result["image_password"] = image_password

    result["config_filename"] = file_name
    result["config_username"] = VMUSERNAME
    result["config_password"] = VMPASSWORD
    result["config_file_loc"] = REPO_PATH
    result['protocol'] = access_protocol
    
    logger.debug("Config file = " + file_name)
    logger.debug("POAP End")
    return result

def process_ignite(info):

    logger.debug("POAP Start")
    logger.debug("Info passed" + str(info))

    # init result object
    result = {}
    result, match_response = match_info(result,info)
    
    # id is got from searched in Rules DB; remove this when that function is added
    #cfg_id = 3

    file_name = build_config(match_response["CFG_ID"], match_response["FABRIC_ID"], match_response["SWITCH_ID"])

    if file_name == None:
        result["err_msg"] = "Error in Config ID = " + str(match_response["CFG_ID"])
        return result
    
    insert_deployed_fabric_stats(match_response, info["system_id"], file_name)
    
    image_name = ''
    imageserver_ip = ''
    image_username = ''
    image_password = ''
    access_protocol = ''
    # Getting default values from json
    for img in image_objects:
        if img['image_profile_name'] == 'default_image':
            image_name = img['image']
            imageserver_ip = img['imageserver_ip']
            image_username = img['username']
            image_password = img['password']
            access_protocol = img['access_protocol']
    # For Valid Fabric
    if match_response["FABRIC_ID"] != INVALID:
        fabric_obj = Fabric.objects.get(id = match_response["FABRIC_ID"])
        img_detail = json.loads(fabric_obj.image_details)
        if bool(img_detail):
            switch = match_response["SWITCH_ID"]
            topo_id = fabric_obj.topology.id
            topology_obj = Topology.objects.get(id=topo_id)
            topology = json.loads(topology_obj.topology_json)
            image = ' '
            type = swtType(switch,topology, fabric_obj.name, match_response["REPLICA_NUM"])
            if type != INVALID:
                image = img_detail[type]
                try:
                    for detail in image_objects:
                        if detail['image_profile_name'] == image:
                            image_name = detail['image']
                            imageserver_ip = detail['imageserver_ip']
                            image_username = detail['username']
                            image_password = detail['password']
                            access_protocol = detail['access_protocol']
                except:
                    logger.error('Failed to read image details')
    # If anything fails, Providing Default(worst case)
    if image_name =='' or imageserver_ip=='' or image_username=='' or image_password=='' or access_protocol=='':
        image_name = DEFAULT_SWITCH_IMAGE_NAME
        imageserver_ip = "172.31.216.138"
        image_username = "root"
        image_password = "cisco123"
        access_protocol = "scp"

    result = fillResult(result,file_name,image_name,imageserver_ip,image_username,image_password,access_protocol)
    #clear_repo(result["config_file_loc"])
    return result

def match_info(result,info):
    '''
    matching fabric or discovery rules
    '''
    result["status"] = False
    result["err_msg"] = ""
    result["config_filename"] = ""

    # first search in fabric specific ruledb
    match_response = match_fabric_rules(info)
    
    # if not found, search in global discovery ruledb
    if match_response["CFG_ID"] == INVALID:
        logger.error("No match in Fabric RuleDB")
        match_response = match_discovery_rules(info)
        
        if match_response["CFG_ID"] == INVALID:
            logger.error("No match in Discovery RuleDB")
            result["err_msg"] = "Did not find matching rule"
        
    return result, match_response


def insert_deployed_fabric_stats(match_response, system_id, file_name):
    '''
    updating DeployedFabricStats on successful CDP request.
    '''
    
    DeployedFabricStats.objects.filter(system_id =system_id).delete()
    deployed_stats = DeployedFabricStats()
    deployed_stats.fabric_id = match_response["FABRIC_ID"]
    deployed_stats.replica_num = match_response["REPLICA_NUM"]
    deployed_stats.switch_name = match_response["SWITCH_ID"]
    deployed_stats.config_id = match_response["CFG_ID"]
    deployed_stats.booted = True
    deployed_stats.config_name =  Configuration.objects.get(id = match_response["CFG_ID"]).name
    deployed_stats.discoveryrule_id = match_response["DISCOVERYRULE_ID"]
    deployed_stats.system_id = system_id
    deployed_stats.match_type = match_response["MATCH_TYPE"]
    deployed_stats.configuration_generated = file_name
    try: 
        deployed_stats.save()
        logger.info("DeployedFabricStats DB Updated successfull.")
        return True
    except:
        logger.info("DeployedFabricStats DB Failed to Update.")
        return False
    

def clear_repo(repo_path):
    for file_name in os.listdir(repo_path):
        if file_name.startswith('.'):
            file_path = os.path.join(repo_path, file_name)
            if os.path.isfile(file_path):
                os.unlink(file_path)

