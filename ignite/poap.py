from configuration.config import build_config
from discoveryrule.discoveryrule import match_discovery_rules
from fabric.const import INVALID
from fabric.fabric_rule import match_fabric_rules
from collection.collection import generate_collection_value
import os

import logging
logger = logging.getLogger(__name__)


def process_poap(info):

    logger.debug("POAP Start")
    logger.debug("Info passed" + str(info))

    # init result object
    result = {}
    result["status"] = False
    result["err_msg"] = ""
    result["filename"] = ""
#    generate_collection_value(6,1,"arun")
    # first search in fabric specific ruledb
    match_response = match_fabric_rules(info)
    
    # if not found, search in global discovery ruledb
    cfg_id = match_response["CFG_ID"]
    fabric_id = match_response["FABRIC_ID"]
    switch_name = match_response["SWITCH_ID"]

    if cfg_id == INVALID:
        logger.error("No match in Fabric RuleDB")

        cfg_id = match_discovery_rules(info)

        if cfg_id == 0:
            logger.error("No match in Discovery RuleDB")
            result["err_msg"] = "Did not find matching rule"
            return result

        fabric_id = -1
        switch_name = info['system_id']

    logger.info("Matched Config ID =" + str(cfg_id))

    # id is got from searched in Rules DB; remove this when that function is added
    #cfg_id = 3

    file_name = build_config(cfg_id, fabric_id, switch_name)

    if file_name == None:
        result["err_msg"] = "Error in Config ID = " + str(cfg_id)
        return result

    result["status"] = True
    result["config_filename"] = file_name
    result["imagename"] = "6.1.2.I3.2"
    result["imageserver"] = "172.31.216.138"
    result["config_username"] = "vmignite"
    result["config_password"] = "cisco123"
    result["config_file_loc"] = os.getcwd() + "/repo/"
    logger.debug("Config file = " + file_name)
    logger.debug("POAP End")
    
    clear_repo(result["config_file_loc"])
    
    return result

def clear_repo(repo_path):
    for file_name in os.listdir(repo_path):
        if file_name.startswith('.'):
            file_path = os.path.join(repo_path, file_name)
            if os.path.isfile(file_path):
                os.unlink(file_path)

