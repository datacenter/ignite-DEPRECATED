import copy
import json
import os
import os.path
import subprocess
from datetime import datetime

from models import Configlet, Configuration
from pool.pool import generate_pool_value
from fabric.fabric_rule import generate_instance_value
from fabric.const import BUILD_PROFILE, BUILD_CONFIG, BUILD_OFF, BUILD_ON, CONFIG_ON_EXT, CONFIG_OFF_EXT
from fabric_profile.models import FabricProfile, ProfileTemplate
from server_configuration import PROJECT_DIR, REPO

import logging
logger = logging.getLogger(__name__)

BASE_PATH = os.getcwd() + PROJECT_DIR + REPO
    

def copy_file(dst_path, src_path):
    dfh = open(dst_path, 'w')
    sfh = open(src_path, 'r')
    for line in sfh.readlines():
        dfh.write(line)
    dfh.close()
    sfh.close()
    logger.debug("Copy file %s to %s" %(src_path, dst_path))

def build_file(whole_id, fabric_id, switch_name, file_path = "", build_method = BUILD_CONFIG, build_type = BUILD_ON, build_new_config = False):
    profile = False
    first_part = True
    module = 'Configuration'
    if build_method == BUILD_PROFILE:
        profile = True
	module = 'Profile'
    
    logger.debug(BASE_PATH)

    file_name = ""
    if not profile:
        if build_type == BUILD_ON:
            file_name = switch_name + CONFIG_ON_EXT
        else:
            file_name = switch_name + CONFIG_OFF_EXT
        file_path = BASE_PATH + file_name

    logger.debug("File path = " + file_path)

    if not profile:
        if not build_new_config:
            off_file_path = BASE_PATH + switch_name + CONFIG_OFF_EXT
            if os.path.isfile(file_path):
                file_mod_time =  os.path.getmtime(file_path)
                if os.path.isfile(off_file_path):
                    off_file_mod_time = os.path.getmtime(off_file_path)
                    if (file_mod_time < off_file_mod_time):
                        logger.debug("User build config file is more recently modified")
                        copy_file(file_path, off_file_path)
                    return file_name
                logger.debug("config file exist")
                return file_name
            if os.path.isfile(off_file_path):
                logger.debug("User build config file exist")
                copy_file(file_path, off_file_path)
                return file_name

    try:
	if profile:
            whole = FabricProfile.objects.get(pk=whole_id)
	else:
            whole = Configuration.objects.get(pk=whole_id)
    except Configuration.DoesNotExist:
        logger.error("Invalid %s ID = %s" %(module,str(whole_id)))
        return None

    
    if whole.submit == "false":
        logger.error("%s ID %s is not ready for use" %(module, str(whole_id)))
        return None

    logger.debug("Building %s, %s ID = %s Fabric Id = %s Switch Name %s" %(module, module, str(whole_id), str(fabric_id), switch_name))

    # params need to be stored across configlets
    param_values = {}

    if profile:
        fh = open(file_path, 'a')
    else:
        fh = open(file_path, 'w')

    for construct in json.loads(whole.construct_list):
	if profile:
            if first_part:
		first_part = False
	    else:
		fh.write(',')
            part_id = construct['template_id']
            logger.debug("Template ID = " + str(part_id))
        else:
	    part_id = construct['configlet_id']
        logger.debug("Configlet ID = " + str(part_id))

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
                

        if not expand_part(fh, part_id, param_values, profile):
            logger.error("Invalid %s ID = %s" %(module, str(part_id)))
            os.remove(file_path)
            return None
    
    fh.close()
    return file_name

def expand_part(fh, part_id, param_values, profile):
    try:
        if profile:
            part = ProfileTemplate.objects.get(pk=part_id)
        else:
            part = Configlet.objects.get(pk=part_id)
    except Configlet.DoesNotExist:
        return False

    part_type = 'template'
    if not profile:
        part_type = part.config_type

    logger.debug("Configlet type  = " + part_type)
    logger.debug("Configlet path  = " + str(part.config_path))

    if part_type == 'script':
        dt = datetime.now() 
        script_path = BASE_PATH + "." +  part.name +"_" + str(dt.microsecond) + ".py"
        logger.debug("Temp script name = " + script_path)
        script_fh = open(script_path, "w")

    if not profile:
        # write a comment about upcoming config
        fh.write("!\n! " + part.name + " config\n!\n")
        fh.flush()
        logger.debug("Expanded Configlet =")

    for line in part.config_path.file:
        for key, value in param_values.iteritems():
            #logger.debug("(key, value) = (" + key + ", " + value + ")")
            #replace param with values
            line = line.replace('$$' + key + '$$', value)
        logger.debug(line)
        
        if part_type == 'template':
            # write to config file
            fh.write(line)
        elif part_type == 'script':
            # write to temp script file
            script_fh.write(line)

    if part_type == 'script':
        # execute script & write output to config file
        proc = subprocess.Popen(['python', script_path], stdout=fh)

        #os.remove(script_path)

    return True

    
def auto_generate_value(start_value):
    generate_list=[]
    for i in range(int(start_value),int(start_value)+100):
        generate_list.append(i)        
    return(str(generate_list))
