import copy
import json
import os
import os.path
import subprocess
from datetime import datetime

from models import Configlet, Configuration
from pool.pool import generate_pool_value
from fabric.fabric_rule import generate_instance_value

import logging
logger = logging.getLogger(__name__)

BASE_PATH = os.getcwd() + '/repo/'


def build_config(cfg_id, fabric_id, switch_name):
    file_name = switch_name + '.cfg'
    file_path = BASE_PATH + file_name

    logger.debug("File path = " + file_path)

    if os.path.isfile(file_path):
        logger.debug("Config file already exists!")
        #return file_name

    try:
        cfg = Configuration.objects.get(pk=cfg_id)
    except Configuration.DoesNotExist:
        logger.error("Invalid Config ID = " + str(cfg_id))
        return None

    if cfg.submit == "false":
        logger.error("Config ID" + str(cfg_id) + " is not ready for use")
        return None

    logger.debug("Building Config, Config ID = " + str(cfg_id) + " Fabric ID = "
                + str(fabric_id) + " Switch Name = " + switch_name)

    # params need to be stored across configlets
    param_values = {}

    fh = open(file_path, 'w')

    for construct in json.loads(cfg.construct_list):
        cfglt_id = construct['configlet_id']
        logger.debug("Configlet ID = " + str(cfglt_id))

        for param in construct['param_list']:
            logger.debug("Param (Name, Type, Value) = (" + param['param_name']
                        + ", " + param['param_type'] + ", " + param['param_value']
                        + ")")

            if param['param_type'] == 'Fixed':
                param_values[param['param_name']] = param['param_value']
            elif param['param_type'] == 'Value':
                param_values[param['param_name']] = param_values[param['param_value']]
            elif param['param_type'] == 'Instance':
                val = generate_instance_value(param['param_value'], fabric_id, switch_name)

                if val == None:
                    logger.error("Instance returned NULL value")
                    os.remove(file_path)
                    return None

                logger.debug("Instance value = " + val)

                param_values[param['param_name']] = val
            elif param['param_type'] == 'Pool':
                val = generate_pool_value(param['param_value'], fabric_id, switch_name)

                if val == None:
                    logger.error("Pool returned NULL value")
                    os.remove(file_path)
                    return None

                param_values[param['param_name']] = val
            elif param['param_type'] == 'Autogenerate':
                param_values[param['param_name']] = auto_generate_value(param['param_value'])
                

        if not expand_configlet(fh, cfglt_id, param_values):
            logger.error("Invalid Configlet ID = " + str(cfglt_id))
            os.remove(file_path)
            return None

    return file_name

def expand_configlet(fh, cfglt_id, param_values):
    try:
        cfglt = Configlet.objects.get(pk=cfglt_id)
    except Configlet.DoesNotExist:
        return False

    cfglt_type = cfglt.config_type

    logger.debug("Configlet type  = " + cfglt_type)
    logger.debug("Configlet path  = " + str(cfglt.config_path))

    if cfglt_type == 'script':
        dt = datetime.now() 
        script_path = BASE_PATH + "." +  cfglt.name +"_" + str(dt.microsecond) + ".py"
        logger.debug("Temp script name = " + script_path)
        script_fh = open(script_path, "w")

    # write a comment about upcoming config
    fh.write("!\n! " + cfglt.name + " config\n!\n")
    fh.flush()
    logger.debug("Expanded Configlet =")

    for line in cfglt.config_path.file:
        for key, value in param_values.iteritems():
            #logger.debug("(key, value) = (" + key + ", " + value + ")")
            #replace param with values
            line = line.replace('$$' + key + '$$', value)
        logger.debug(line)
        
        if cfglt_type == 'template':
            # write to config file
            fh.write(line)
        elif cfglt_type == 'script':
            # write to temp script file
            script_fh.write(line)

    if cfglt_type == 'script':
        # execute script & write output to config file
        proc = subprocess.Popen(['python', script_path], stdout=fh)

        #os.remove(script_path)

    return True

    
def auto_generate_value(start_value):
    generate_list=[]
    for i in range(int(start_value),int(start_value)+100):
        generate_list.append(i)        
    return(str(generate_list))
