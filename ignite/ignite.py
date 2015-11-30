from configuration.config import build_file
from discoveryrule.discoveryrule import match_discovery_rules 
from fabric.const import INVALID
from fabric.fabric_rule import match_fabric_rules 
from pool.pool import generate_pool_value
import os
from image_profile.models import ImageProfile
from image_profile.ImageProfileSerializer import ImageProfileGetSerializer
from fabric.models import DeployedFabricStats, FabricRuleDB, Fabric, Topology
from configuration.models import Configuration
from fabric.const import *
import json
import re
from server_configuration import VMUSERNAME, VMPASSWORD, PROJECT_DIR, REPO, DEFAULT_SWITCH_IMAGE_NAME
import datetime
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

REPO_PATH = os.getcwd() + PROJECT_DIR + REPO

def swtType(switch, topology, fab_name, replica_num):
    for sw in topology[SPINE_LIST]:
        switchName = fab_name+'_'+str(replica_num)+'_'+sw[SWITCH_NAME]
        if str(switch) == switchName:
            return SPINE_IMAGE_PROFILE
    for sw in topology[LEAF_LIST]:
        switchName = fab_name+'_'+str(replica_num)+'_'+sw[SWITCH_NAME]
        if str(switch) == switchName:
            return LEAF_IMAGE_PROFILE
    return INVALID

def fillResult(result,file_name,image_data):
    result["status"] = True
    result["imagename"] = image_data['image']
    result["imageserver"] = image_data['imageserver_ip']
    result["image_username"] = image_data['username']
    result["image_password"] = image_data['password']
    result['protocol'] = image_data['access_protocol']

    result["config_filename"] = file_name
    result["config_username"] = VMUSERNAME
    result["config_password"] = VMPASSWORD
    result["config_file_loc"] = REPO_PATH
    
    logger.debug("Config file = " + file_name)
    logger.debug("POAP End")
    return result

def fill_image(image='', imageserver_ip='', username='',password='',access_protocol=''):
    image_data = {}
    image_data['image'] = image
    image_data['imageserver_ip'] = imageserver_ip
    image_data['username'] = username
    image_data['password'] = password
    image_data['access_protocol'] = access_protocol
    return image_data

def process_ignite(info):

    logger.debug("POAP Start")
    logger.debug("Info passed" + str(info))
    
    build_new_config = False

    # init result object
    result = {}
    result, match_response = match_info(result,info)
    
    # id is got from searched in Rules DB; remove this when that function is added
    #cfg_id = 3

    if (match_response["FABRIC_ID"] == INVALID):
        build_new_config = True
    
    file_name = build_file(match_response["CFG_ID"], match_response["FABRIC_ID"], match_response["SWITCH_ID"], build_new_config)

    if file_name == None:
        result["err_msg"] = "Error in Config ID = " + str(match_response["CFG_ID"])
        return result
    
    file_path = REPO_PATH + file_name 
    sanitize_repo(file_path)
    
    status = insert_deployed_fabric_stats(match_response, info["system_id"], file_name)
    if not status:
		result["err_msg"] = 'Failed to update stats'
		return result
    
    
#     image_data = fill_image()
    image_data = fill_image(image=DEFAULT_SWITCH_IMAGE_NAME, imageserver_ip="172.31.216.138", username="root",password="cisco123",access_protocol="scp")
    
    # For Valid Fabric
    try:
        if match_response["FABRIC_ID"] != INVALID:
            fabric_obj = Fabric.objects.get(id = match_response["FABRIC_ID"])
            img_detail = json.loads(fabric_obj.image_details)
            if bool(img_detail):
                switch = match_response["SWITCH_ID"]
                
                image_id = INVALID
                for sw_level in img_detail[IMAGE_KEY]:
                    var = fabric_obj.name+"_"+str(match_response["REPLICA_NUM"])+"_"+sw_level[SWITCH_NAME]
                    if var == switch:
                        image_id = sw_level['image_profile']
                if image_id == INVALID:
                    type_name = ''
                    topo_id = fabric_obj.topology.id
                    topology_obj = Topology.objects.get(id=topo_id)
                    topology = json.loads(topology_obj.topology_json)
                    type_name = swtType(switch,topology, fabric_obj.name, match_response["REPLICA_NUM"])
                    if type_name != INVALID:
                        image_id = img_detail[type_name]
                try:
                    image_object = ImageProfile.objects.get(pk=image_id)
                    serializer = ImageProfileGetSerializer(image_object)
                    image_details = serializer.data
                    del image_details['image_profile_name']
                    del image_details['id']
                    image_data = fill_image(**image_details)
                except:
                    logger.error('Failed to read image details')
    except:
        logger.error('Failed to read image details')
    # If anything fails, Providing Default(worst case)
#     if image_name =='' or imageserver_ip=='' or image_username=='' or image_password=='' or access_protocol=='':
#         image_data = fill_image(image=DEFAULT_SWITCH_IMAGE_NAME, imageserver_ip="172.31.216.138", username="root",password="cisco123",access_protocol="scp")

    result = fillResult(result,file_name,image_data)
    #clear_repo(result["config_file_loc"])
    #sanitize_repo(repo_path) 
     
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

def create_stat_obj(match_response, system_id, file_name, pregenerate_flag):
    
    deployed_stats = DeployedFabricStats()
	
    deployed_stats.fabric_id = match_response["FABRIC_ID"]
    deployed_stats.replica_num = match_response["REPLICA_NUM"]
    deployed_stats.switch_name = match_response["SWITCH_ID"]
    deployed_stats.config_id = match_response["CFG_ID"]
 
    deployed_stats.booted = True
    if pregenerate_flag:
        deployed_stats.booted = False
        #deployed_stats.build_time = datetime.datetime.utcnow()
        deployed_stats.build_time = timezone.now()
    else:
        #deployed_stats.boot_time = datetime.datetime.utcnow()
        deployed_stats.boot_time = timezone.now()

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
	
def insert_deployed_fabric_stats(match_response, system_id, file_name, pregenerate_flag = False):
    '''
    updating DeployedFabricStats on successful CDP request.
    '''
    deployed_stats = None
    exist  = False
    switch_name = match_response['SWITCH_ID']
    status = True

    try:
        deployed_stats = DeployedFabricStats.objects.get(switch_name = switch_name)
        exist = True
    except:
        logger.debug("Deployed Stat for switch: %s does not exist" %switch_name) 
    logger.error(exist)
   
    if exist:
        logger.error(pregenerate_flag)
        if pregenerate_flag:
            try:
                deployed_stats.file_name = file_name
                #deployed_stats.build_time = datetime.datetime.utcnow() 
                deployed_stats.build_time = timezone.now() 
                deployed_stats.save()
            except:
                logger.error("Failed to update Build_time for switch %s" %switch_name)
        else:
            deployed_stats.file_name = file_name
            deployed_stats.booted = True
            deployed_stats.boot_time = datetime.datetime.utcnow()
            deployed_stats.boot_time = timezone.now()
            deployed_stats.system_id = system_id
            deployed_stats.match_type = match_response['MATCH_TYPE']
            deployed_stats.discoveryrule_id = match_response['DISCOVERYRULE_ID']
            try:
                deployed_stats.save()
            except:
                logger.error("Failed to update deployed fabric stats for switch: %s" %switch_name)			
                status =  False

    else:
        status = create_stat_obj(match_response, system_id, file_name, pregenerate_flag)

    return status


def clear_repo(repo_path):
    for file_name in os.listdir(repo_path):
        if file_name.startswith('.'):
            file_path = os.path.join(repo_path, file_name)
            if os.path.isfile(file_path):
                os.unlink(file_path)

def sanitize_repo(file_path):
    if os.path.isfile(file_path):
        with open(file_path, 'r') as fh:
            data = (fh.read()).replace('\r', '')
        with open(file_path, 'w') as fh:
            fh.write(data)

         
