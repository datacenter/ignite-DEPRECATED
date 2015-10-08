__author__  = "arunrajms"

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
import ast
import json
import re
import logging

from models import DiscoveryRule
from serializer.DiscoveryRuleSerializer import DiscoveryRuleSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleGetSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleGetDetailSerializer

from usermanagement.utils import RequestValidator
from django.http import JsonResponse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from pprint import *
from fabric.const import FABRIC_MATCH_RESPONSE,INVALID, MATCH_TYPE_NEIGHBOUR, MATCH_TYPE_SYSTEM_ID
from fabric.models import Fabric
from fabric.fabric_rule import build_fabric_map, build_vpc_detail

logger = logging.getLogger(__name__)


def regex_match(condition,string,value):
    if(condition=='contain'):
        if(re.search(string,value)==None):
            return 0
        return 1
    if(condition=='no_contain'):
        if(re.search(string,value)==None):
            return 1
        return 0
    if(condition=='match'):
        string='^'+string+'$'
        if(re.search(string,value)==None):
            return 0
        return 1
    if(condition=='no_match'):
        string='^'+string+'$'
        if(re.search(string,value)==None):
            return 1
        return 0
    if(condition=='any'):
        return 1
    return 1

def match_none(subrule,neighbor_list):

    if(subrule['rn_condition']=='none'):
        for neigh in neighbor_list:
            if (regex_match('contain',subrule['rn_string'],neigh['remote_node'])):
                return 0
    if(subrule['rp_condition']=='none'):
        for neigh in neighbor_list:
            if (regex_match('contain',subrule['rp_string'],neigh['remote_port'])):
                return 0
    if(subrule['lp_condition']=='none'):
        for neigh in neighbor_list:
            if (regex_match('contain',subrule['lp_string'],neigh['local_port'])):
                return 0
    return 1
    

def match_discovery_rules(cdp_nei_list):
    neighbor_list = cdp_nei_list['neighbor_list']
    discoveryrule = DiscoveryRule.objects.exclude(match='serial_id').order_by('priority')
    match_response = dict(FABRIC_MATCH_RESPONSE)
    config_id = INVALID
    
    if len(neighbor_list) > 0:
        for single_obj in discoveryrule.iterator():
            subrules_list = json.loads(single_obj.subrules)
            all_subrule_match_flag = 0
            for subrule in subrules_list:
                subrule_match_flag = 0
                
                if(subrule['rn_condition']=='none' or subrule['rp_condition']=='none' or subrule['lp_condition']=='none'):
                    subrule_match_flag = match_none(subrule,neighbor_list)
                    logger.debug("Subrule has a none condition. Checked it in all neighbor_list and the result is: "+str(bool(subrule_match_flag)))
                else:            
                    for neigh in neighbor_list:
                        if(regex_match(subrule['rn_condition'],subrule['rn_string'],neigh['remote_node'])):
                            if(regex_match(subrule['rp_condition'],subrule['rp_string'],neigh['remote_port'])):
                                if(regex_match(subrule['lp_condition'],subrule['lp_string'],neigh['local_port'])):
                                    subrule_match_flag = 1
                                    logger.debug("Matched a neighbor_list "+str(neigh)+" with subrule "+str(subrule))
                                    break
                
                if single_obj.match == 'all':
                    if subrule_match_flag == 0:
                        all_subrule_match_flag = 0
                        break
                    else:
                        all_subrule_match_flag = 1
                elif single_obj.match == 'any':
                    if subrule_match_flag == 1:
                        all_subrule_match_flag = 1
                        break

            if all_subrule_match_flag == 1:
                config_id = single_obj.config_id
                match_response["DISCOVERYRULE_ID"] = single_obj.id
                match_response["MATCH_TYPE"] = MATCH_TYPE_NEIGHBOUR
                logger.debug("The matching discoveryrule id is: "+str(single_obj.id))
                break
        
    if config_id==INVALID:
        discoveryrule = DiscoveryRule.objects.filter(match='serial_id').order_by('priority')
        serial_id = cdp_nei_list['system_id']
        for single_obj in discoveryrule.iterator():
            subrules_list = ast.literal_eval(single_obj.subrules)
            for subrule_serial_id in subrules_list:
                if serial_id == subrule_serial_id:
                    config_id=single_obj.config_id
                    match_response["DISCOVERYRULE_ID"] = single_obj.id
                    match_response["MATCH_TYPE"] = MATCH_TYPE_SYSTEM_ID
                    logger.debug("The matching discoveryrule with serial-id is: "+str(single_obj.id))
                    break
            if config_id!=INVALID:
                break
    logger.debug("The configuration id is: "+str(config_id))
    if config_id != INVALID: 
        match_response["CFG_ID"] = config_id
        match_response["SWITCH_ID"] = cdp_nei_list['system_id']
        # calling build functions from fabric
        dis_obj = DiscoveryRule.objects.get(id = match_response["DISCOVERYRULE_ID"])
        if dis_obj.fabric_id != INVALID:
            # filling match_response for serialId match
            match_response['FABRIC_ID'] = dis_obj.fabric_id
            match_response['REPLICA_NUM'] = dis_obj.replica_num
            match_response['SWITCH_ID'] = dis_obj.switch_name
            
            fabric_obj = Fabric.objects.get(id = dis_obj.fabric_id)
            fabric_name = fabric_obj.name
            fabric_name = fabric_name + "_" + str(dis_obj.replica_num) + "_"
            topology_obj = fabric_obj.topology
            local_node = dis_obj.switch_name
            build_fabric_map(fabric_name, topology_obj, local_node)
            try:
                build_vpc_detail(local_node)
            except KeyError,e:
                logger.error("Key:" + str(e) + " not found")
                return match_response
    
    return match_response
