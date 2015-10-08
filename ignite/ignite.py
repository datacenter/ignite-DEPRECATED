from configuration.config import build_config
from discoveryrule.discoveryrule import match_discovery_rules 
from fabric.const import INVALID
from fabric.fabric_rule import match_fabric_rules 
from pool.pool import generate_pool_value
import os
from fabric.models import DeployedFabricStats, FabricRuleDB, Fabric
from configuration.models import Configuration
from fabric.const import *
 
import logging
logger = logging.getLogger(__name__)


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

    result["status"] = True
    result["config_filename"] = file_name
    result["imagename"] = "6.1.2.I3.2"
    result["imageserver"] = "172.31.216.138"
    result["config_username"] = "vmignite"
    result["config_password"] = "cisco123"
    result["config_file_loc"] = os.getcwd() + "/repo/"
    logger.debug("Config file = " + file_name)
    logger.debug("POAP End")
    
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

