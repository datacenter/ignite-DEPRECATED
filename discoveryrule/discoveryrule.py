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
    config_id=0
    
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
                logger.debug("The matching discoveryrule id is: "+str(single_obj.id))
                break
        
    if config_id==0:
        discoveryrule = DiscoveryRule.objects.filter(match='serial_id').order_by('priority')
        serial_id = cdp_nei_list['system_id']
        for single_obj in discoveryrule.iterator():
            subrules_list = ast.literal_eval(single_obj.subrules)
            for subrule_serial_id in subrules_list:
                if serial_id == subrule_serial_id:
                    config_id=single_obj.config_id
                    logger.debug("The matching discoveryrule with serial-id is: "+str(single_obj.id))
                    break
            if config_id!=0:
                break
    logger.debug("The configuration id is: "+str(config_id))
    
    return config_id
