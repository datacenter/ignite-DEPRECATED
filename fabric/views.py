from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404, JsonResponse
from usermanagement.utils import RequestValidator
from django.contrib.auth.models import User
import json
import logging
import os
import string
from django.core.servers.basehttp import FileWrapper
import re
from collections import Counter
import glob
import gzip

#Imports from user defined modules
from models import Topology, Fabric, FabricRuleDB, DeployedFabricStats
from fabric_rule import generate_fabric_rules, delete_fabric_rules, generate_config, build_fabric_profiles
from serializer.topology_serializer import TopologyGetSerializer, TopologySerializer, TopologyGetDetailSerializer, TopologyPutSerializer
from serializer.fabric_serializer import FabricSerializer, FabricGetSerializer, FabricGetDetailSerializer, FabricPutSerializer
from serializer.fabric_serializer import FabricRuleDBGetSerializer, ImagePostSerializer, ImageDetailSerializer, ProfilesDictSerializer
from serializer.deployed_serializer import DeployedFabricGetSerializer, DeployedFabricDetailGetSerializer
from configuration.models import Configuration
from discoveryrule.models import DiscoveryRule
from fabric.const import INVALID, LOG_SEARCH_COL, IMAGE_KEY, PROFILE_KEY, CONFIG_KEY,LEAF_LIST, \
                            SPINE_LIST, LINK_LIST, SWITCH_NAME, SWITCH_1, SWITCH_2, CONFIGURATION_ID
from discoveryrule.models import DiscoveryRule
from discoveryrule.serializer.DiscoveryRuleSerializer import DiscoveryRuleGetDetailSerializer
from fabric.image_profile import image_objects
from server_configuration import PROJECT_DIR, REPO, REMOTE_SYSLOG_PATH


logger = logging.getLogger(__name__)

POAP_LOG_START = 'Started the execution at do_it function'
POAP_LOG_END = 'POAP End'
SYSLOG_PATH = '/var/log/syslog*'

BASE_PATH = os.getcwd() + PROJECT_DIR + REPO


# Create your views here.

def findDuplicate(data_list, key):
    item_list = []
    dup_items = []
    for switch in data_list:
        item_list.append(switch[key])
    dup_items = [k for k,v in Counter(item_list).items() if v>1]
    if len(dup_items)>0:
        error_string = ','.join(str(item) for item in dup_items)
        err_msg = ' '+error_string+' repeated.'
        logger.error(err_msg)
        return err_msg, True
    return "", False
    
def uniqueSystenmId(data, fabric_id):
    err_msg = ""
    for sys_id in data:
        dis_rule_name = 'serial_'+str(sys_id['system_id'])
        old_dis_rule = DiscoveryRule.objects.filter(name= dis_rule_name)
        if old_dis_rule:
            obj = DiscoveryRule.objects.get(name= dis_rule_name)
            if fabric_id != obj.fabric_id:
                err_msg = sys_id['system_id']+' is assigned for '+obj.switch_name
                break
    return err_msg
            
def add_dis_rule(data, success, resp, fabric_id, switch_to_configuration_id):
    try:
        sys_id_obj = data['system_id']
        regex  =  data['name'] + '(_)([1-9][0-9]*)(_)([a-zA-Z]*-[1-9])'
        dis_bulk_obj = []
        for switch_systemId_info in sys_id_obj:
            switch_name = (re.search(regex, switch_systemId_info['name'])).group(4)
            replica_num = int((re.search(regex, switch_systemId_info['name'])).group(2))
            system_id = switch_systemId_info['system_id']
            discoveryrule_name = 'serial_'+switch_systemId_info['system_id']
            dis_rule_obj = DiscoveryRule()
            dis_rule_obj.priority = 100
            dis_rule_obj.name = discoveryrule_name
            dis_rule_obj.config_id = switch_to_configuration_id[switch_name]
            dis_rule_obj.match = 'serial_id'
            dis_rule_obj.subrules = [system_id]
            dis_rule_obj.fabric_id = fabric_id
            dis_rule_obj.replica_num = replica_num
            dis_rule_obj.switch_name = switch_systemId_info['name']
            dis_bulk_obj.append(dis_rule_obj)
#                     dis_rule_obj.save()
        return success, resp, dis_bulk_obj
    except:
        success = False
        logger.error('Failed to update discoveryRule DB with system_id rule for fabric_id: '+\
                     str(fabric_id))
        resp['Error'] = 'Failed to update DiscoveryRule DB' 
        return success, resp, dis_bulk_obj
                    
def getFile_list(syslog_path):
    fName_list = []
    try:
        for fName in glob.glob(syslog_path):
            fName_list.append(fName)
        fName_list.sort(reverse=True)
    except:
        pass
    return fName_list

def getConfig_id(data_json, spine_list, leaf_list):
    switch_with_id = {}
    complete_switch_list = spine_list.union(leaf_list)
    try:
        for sw_name in complete_switch_list:
            found = False
            for item in data_json[CONFIG_KEY]:
                if item[SWITCH_NAME] == str(sw_name):
                    found = True
                    switch_with_id[sw_name] = item[CONFIGURATION_ID]
            if not(found):
                if sw_name in spine_list:
                    switch_with_id[sw_name] = data_json['spine_config_id']
                elif sw_name in leaf_list:
                    switch_with_id[sw_name] = data_json['leaf_config_id']
        return switch_with_id
    except:
        logger.error('Got error while parsing config json')
        return switch_with_id

def getSwitch_list(topology_json, key):
    sw_set = set()
    for item in topology_json[key]:
        sw_set.add(str(item[SWITCH_NAME]))
    return sw_set

def fill_config_used(id, incr_val):
    try:
        config_obj = Configuration.objects.get(id = id)
        config_obj.used += incr_val
        config_obj.save()
        return True
    except:
        return False

def update_config_count(config_json, spine_list, leaf_list, key):
    leaf_count = 0
    spine_count = 0
    err = {}
    try:
        for config in config_json[CONFIG_KEY]:
            try:
                if config[SWITCH_NAME] in spine_list:
                    spine_count += 1
                elif config[SWITCH_NAME] in leaf_list:
                    leaf_count += 1
                if key:
                    status = fill_config_used(config['configuration_id'], 1)
                else:
                    status = fill_config_used(config['configuration_id'], -1)        
            except:
                err['Error'] = 'Configuration not found wiht id :' +str(config['configuration_id'])
                logger.error(err['Error'])
                return err, False
        leaf_common_count = len(leaf_list) - leaf_count
        if not key:
            leaf_common_count = 0 - (leaf_common_count)
        status = fill_config_used(config_json['leaf_config_id'], leaf_common_count)
        spine_common_count = len(spine_list) - spine_count
        if not key:
            spine_common_count = 0- spine_common_count
        status = fill_config_used(config_json['spine_config_id'], spine_common_count)
        return err, True
    except:
        err['Error'] = 'Failed to update Config used count variable'
        logger.error(err['Error'])
        return err, False


class JSONResponse(HttpResponse):
    
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class TopologyList(APIView):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(TopologyList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        To fetch the list of Topologies
        """
        topology_list = Topology.objects.filter(status = True).order_by('name')
        serializer = TopologyGetSerializer(topology_list, many=True)
        index = 0
        for item in serializer.data:
            try:
                item['user_name'] = User.objects.get(id=topology_list[index].user_id).username
            except User.DoesNotExist:
                raise Http404
            index = index + 1
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        To add a new Topology
        ---
  serializer: "TopologySerializer"

        """
        serializer = TopologySerializer(data=request.data)
        me = RequestValidator(request.META)
        if serializer.is_valid():
            topology_obj = Topology()
            topology_obj.user_id = me.user_is_exist().user_id
            topology_obj.name = request.data['name']
            topology_obj.submit = request.data['submit']
            topology_obj.topology_json = json.dumps(request.data['topology_json'])
            try:
                topology_obj.config_json = json.dumps(request.data['config_json'])
            except:
                topology_obj.config_json = json.dumps([])
            try:
                topology_obj.defaults = json.dumps(request.data['defaults'])
            except:
                topology_obj.defaults = json.dumps({})
            topology_obj.save()
            serializer = TopologyGetSerializer(topology_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TopologyDetail(APIView):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(TopologyDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, id):
        try:
            return Topology.objects.get(pk=id)
        except Topology.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        """
        To fetch a particular topology
        """
        topology = self.get_object(id)
        serializer = TopologyGetDetailSerializer(topology)
        topo_detail = serializer.data
        topo_detail['topology_json'] = json.loads(topo_detail['topology_json'])
        try:
            topo_detail['config_json'] = json.loads(topo_detail['config_json'])
        except:
            topo_detail['config_json'] = []
        try:
            topo_detail['defaults'] = json.loads(topo_detail['defaults'])
        except:
            topo_detail['defaults'] = {}
        return Response(topo_detail)

    def put(self, request, id, format=None):
        """
        To edit an existing Topology
        
        ---
  serializer: "TopologyPutSerializer"

        """
        topology = self.get_object(id)
        if request.data['name'] == self.get_object(id).name:
            serializer = TopologyPutSerializer(data=request.data)
        else:
            serializer = TopologySerializer(data=request.data)
        me = RequestValidator(request.META)
        if serializer.is_valid():
            count = Fabric.objects.filter(topology = topology).count()
            if count:
                logger.error("Fail to update Topology id " + str(id) + ", Number of Fabrics using it as base topology-" + str(count))
            else:
                topology_obj = topology
                topology_obj.user_id = me.user_is_exist().user_id
                topology_obj.name = request.data['name']
                topology_obj.submit = request.data['submit']
                topology_obj.topology_json = json.dumps(request.data['topology_json'])
                try:
                    topology_obj.config_json = json.dumps(request.data['config_json'])
                except:
                    topology_obj.config_json = json.dumps([])
                try:
                    topology_obj.defaults = json.dumps(request.data['defaults'])
                except:
                    topology_obj.defaults =json.dumps({})
                topology_obj.save()
                serailizer = TopologyGetDetailSerializer(topology_obj)
                resp = serailizer.data
                resp['topology_json'] = json.loads(resp['topology_json'])
                try:
                    resp['config_json'] = json.loads(resp['config_json'])
                except:
                    resp['config_json'] = []
                try:
                    resp['defaults'] = json.loads(resp['defaults'])
                except:
                    resp['defaults'] = {}
                return Response(resp)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        To delete a topology
        """
        topology = self.get_object(id)
        count = Fabric.objects.filter(topology = topology).count()
        if count:
            logger.error("Fail to delete Topology id " + str(id) + ", " +\
            str(count) + " Fabrics are using it as base topology")
            return Response("Topology is in use", status=status.HTTP_400_BAD_REQUEST)
        topology.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FabricList(APIView):
   
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        To fetch the list of Fabrics
        """
        fabric_list = Fabric.objects.filter(status = True).order_by('id')
        serializer = FabricGetSerializer(fabric_list, many=True)
        index = 0
        for item in serializer.data:
            item['topology_name'] = fabric_list[index].topology.name
            item['topology_id']  = fabric_list[index].topology.id
        
            try:
                item['user_name']   = User.objects.get(id=fabric_list[index].user_id).username
            except User.DoesNotExist:
                raise Http404
            index = index + 1
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        To add a new Fabric
        ---
  serializer: "FabricSerializer"

        """
        success = True
        resp = {}
        resp['Error'] = ' '
        serializer = FabricSerializer(data=request.data)
        topology = Topology.objects.get(id=request.data['topology_id'])
        topology_json = json.loads(topology.topology_json)
        me = RequestValidator(request.META)
        if serializer.is_valid():
            if request.data['instance'] < 1:
                logger.error("Fabric Instances cannot be less than 1")
            else:
                fabric_obj = Fabric()
                find_dup_data = {'name' : [{'system_id':'system_id'},{'config_json':CONFIG_KEY}, \
                                            {'image_details':IMAGE_KEY},{'profiles':PROFILE_KEY}],\
                                 'system_id':[{'system_id':'system_id'}]}
                for key,val in find_dup_data.iteritems():
                    for value in val:
                        data_list = []
                        try:
                            if value.keys()[0] == 'system_id':
                                data_list = request.data[value.values()[0]]
                            else:
                                data_list = request.data[value.keys()[0]][value.values()[0]]
                            err_msg, isError = findDuplicate(data_list, key)
                            if isError:
                                resp['Error'] = err_msg
                                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                        except:pass
                err = uniqueSystenmId(request.data['system_id'],fabric_obj.id)
                if err != "":
                    resp['Error'] = err
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                fabric_obj.name = request.data['name']
                fabric_obj.user_id = me.user_is_exist().user_id
                fabric_obj.topology = topology
                topology.used += 1
                topology.save()
                fabric_obj.instance = request.data['instance']
                fabric_obj.validate = request.data['validate']
                fabric_obj.locked = request.data['locked']
                if request.data['config_json']['leaf_config_id'] == INVALID or \
                    request.data['config_json']['spine_config_id'] == INVALID or \
                    request.data['config_json']['leaf_config_id'] == '-1' or\
                     request.data['config_json']['spine_config_id'] == '-1':
                    resp['Error'] = 'Config Id can not be None at Tier Level'
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                # getting config id for every switch and updatin config used count
                leaf_set = set()
                spine_set = set()
                leaf_set = getSwitch_list(topology_json, LEAF_LIST)
                spine_set = getSwitch_list(topology_json, SPINE_LIST)
                switch_to_configuration_id = getConfig_id(request.data['config_json'], spine_set,leaf_set)
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                errmsg, err_bool = update_config_count(request.data['config_json'], spine_set, leaf_set, True) 
                if not(err_bool):
                    return Response(errmsg, status=status.HTTP_400_BAD_REQUEST)
                fabric_obj.submit = request.data['submit']
                try:
                    fabric_obj.system_id = json.dumps(request.data['system_id'])
                except:
                    fabric_obj.system_id = []
                try:
                    fabric_obj.profiles = json.dumps(request.data['profiles'])
                except:
                    fabric_obj.profiles = json.dumps({})
                    
                try:   # fill image details
                    fabric_obj.image_details = json.dumps(request.data['image_details'])
                    if request.data['image_details']['leaf_image_profile'] == '-1' or \
                       request.data['image_details']['spine_image_profile'] == '-1' or \
                       request.data['image_details']['leaf_image_profile'] == INVALID or \
                       request.data['image_details']['spine_image_profile'] == INVALID : 
                        resp['Error'] = 'Image Profile can not be None at Tier Level'
                        return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                except:
                    fabric_obj.image_details = json.dumps({})
                try:  # save object
                    fabric_obj.save()
                except:
                    logger.error("Failed to create Fabric: " + fabric_obj.name)
                    resp['Error'] = 'Failed to create Fabric' 
                    return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
                                
                # filling discovery rule with system_id
                success, resp, dis_bulk_obj = add_dis_rule(request.data,success,resp,fabric_obj.id,switch_to_configuration_id )
                
                if success:   
                    if (generate_fabric_rules(request.data['name'],\
                    request.data['instance'], fabric_obj, switch_to_configuration_id,\
                    topology_json)):
                        serializer = FabricGetSerializer(fabric_obj)
                        logger.info("Successfully created Fabric id: " + str(fabric_obj.id))
                        try:
                            for obj in dis_bulk_obj:
                                obj.save()
                        except:
                            logger.error('failed to save dis_rule_obj')
                            resp['Error']='Failed to save DiscoveryRules'
                            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        success = False
                        logger.error("Failed to update FabricRuleDb: " + fabric_obj.name)
                        resp['Error'] = 'Failed to update FabricRule DB'
                        
                    
                if not success:
                    try:
                        DiscoveryRule.objects.filter(fabric_id = fabric_obj.id).delete()
                    except:
                        pass
                    Fabric.objects.filter(id = fabric_obj.id).delete()
                    logger.error("Failed to create Fabric: " + fabric_obj.name)
                    return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
                        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FabricDetail(APIView):
   
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, id):
        try:
            return Fabric.objects.get(pk=id)
        except Fabric.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        """
        To fetch a particular Fabric
        """
        topo_detail = {}
        fabric = self.get_object(id)
        serializer = FabricGetDetailSerializer(fabric)
        data = dict(serializer.data)
        data['config_json'] = json.loads(data['config_json'])
        data['system_id'] = json.loads(data['system_id'])
        try:
            data['image_details'] = json.loads(data['image_details'])
        except:
            data['image_details'] = {}
        try:
            data['profiles'] = json.loads(data['profiles'])
        except:
            data['profiles'] = {}
        try:
            topology = Topology.objects.get(id=fabric.topology.id)
        except Topology.DoesNotExist:
            raise Http404
        
        topology_json = json.loads(topology.topology_json)
        topo_detail.update({'topology_name':topology.name})
        topo_detail.update({'topology_id':topology.id})
        topo_detail.update({'topology_json':topology_json})
        #topology_json['topology_name'] = topology.name
        #topology_json['topology_id']  = topology.id
        data['topology'] = topo_detail

        return Response(data)

    def put(self, request, id, format=None):
        """
        To edit an existing Fabric 
        ---
  serializer: "FabricPutSerializer"

        """
        success = True
        resp = {}
        resp['Error'] = ' '
        fabric_obj = self.get_object(id)
        topology_id = fabric_obj.topology.id
        serializer = FabricPutSerializer(data=request.data)
        if serializer.is_valid():
            if ((request.data['topology_id'] != topology_id) or (fabric_obj.name != request.data['name'])):
                logger.error("Failed to Update Fabric id " + str(id)\
                +" cannot change base Topology or Fabric Name")
            else:
                topology = Topology.objects.get(id=request.data['topology_id'])
                topology_json = json.loads(topology.topology_json)
                me = RequestValidator(request.META)
                fabric_obj.user_id = me.user_is_exist().user_id
                fabric_obj.validate = request.data['validate']
                fabric_obj.locked = request.data['locked']
                find_dup_data = {'name' : [{'system_id':'system_id'},{'config_json':CONFIG_KEY}, \
                                            {'image_details':IMAGE_KEY},{'profiles':PROFILE_KEY}],\
                                 'system_id':[{'system_id':'system_id'}]}
                for key,val in find_dup_data.iteritems():
                    for value in val:
                        try:
                            data_list = []
                            if value.keys()[0] == 'system_id':
                                data_list = request.data[value.values()[0]]
                            else:
                                data_list = request.data[value.keys()[0]][value.values()[0]]
                            err_msg, isError = findDuplicate(data_list, key)
                            if isError:
                                resp['Error'] = err_msg
                                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                        except:pass
                err = uniqueSystenmId(request.data['system_id'], fabric_obj.id)
                if err !="":
                    resp['Error'] = err
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                if request.data['config_json']['leaf_config_id'] == INVALID or \
                    request.data['config_json']['spine_config_id'] == INVALID or \
                    request.data['config_json']['leaf_config_id'] == '-1' or\
                     request.data['config_json']['spine_config_id'] == '-1':
                    resp['Error'] = 'Config Id can not be None at Tier Level'
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                # getting config id for every switch and updatin config used count
                leaf_set = set()
                spine_set = set()
                leaf_set = getSwitch_list(topology_json, LEAF_LIST)
                spine_set = getSwitch_list(topology_json, SPINE_LIST)
                switch_to_configuration_id = getConfig_id(request.data['config_json'], spine_set,leaf_set)
                config_json = json.loads(fabric_obj.config_json)
                errmsg, err_bool = update_config_count(config_json, spine_set, leaf_set, False) 
                if not(err_bool):
                    return Response(errmsg, status=status.HTTP_400_BAD_REQUEST)
                errmsg, err_bool = update_config_count(request.data['config_json'], spine_set, leaf_set, True) 
                if not(err_bool):
                    return Response(errmsg, status=status.HTTP_400_BAD_REQUEST)
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                fabric_obj.submit = request.data['submit']
                fabric_obj.instance = request.data['instance']
                # filling image details
                try: 
                    fabric_obj.image_details = json.dumps(request.data['image_details'])
                    if request.data['image_details']['leaf_image_profile'] == '-1' or \
                       request.data['image_details']['spine_image_profile'] == '-1' or \
                       request.data['image_details']['leaf_image_profile'] == INVALID or \
                       request.data['image_details']['spine_image_profile'] == INVALID : 
                        resp['Error'] = 'Image Profile can not be None at Tier Level'
                        return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                except:
                    pass
                # filling profiles
                try:
                    fabric_obj.profiles = json.dumps(request.data['profiles'])
                except:pass
                
                try:
                    fabric_obj.system_id = json.dumps(request.data['system_id'])
                except:pass
                
                #Add discovery rule
                try:
                    DiscoveryRule.objects.filter(fabric_id=id).delete()
                except:
                    logger.error('Failed to delete Discovery rules with fabric_id:'+str(id))
                    resp['Error'] = ['Failed to delete Discovery rules']
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                
                success, resp, dis_bulk_obj = add_dis_rule(request.data,success,resp,fabric_obj.id,switch_to_configuration_id )
                
                if success:
                    if delete_fabric_rules(id):
                        if (generate_fabric_rules(request.data['name'],\
                            request.data['instance'], fabric_obj, switch_to_configuration_id,\
                            topology_json)):
                            logger.info("Successfully  update Fabric id: " + str(id))
                            serializer = FabricGetDetailSerializer(fabric_obj)
                            data = serializer.data
                            data['config_json'] = json.loads(data['config_json'])
                            try:
                                data['system_id'] = json.loads(data['system_id'])
                            except:
                                data['system_id'] = []
                            try: # image details
                                data['image_details'] = json.loads(data['image_details'])
                            except:
                                data['image_details'] = {}
                            try:
                                data['profiles'] = json.loads(data['profiles'])
                            except:
                                data['profiles'] = {}
                            for obj in dis_bulk_obj:
                                obj.save()
                            fabric_obj.save()
                            return Response(data)
                        else:
                            success = False
                            resp['Error'] = 'Failed to update Fabric'
                            logger.error("Failed to update Fabric id: " + str(id))
                    else:
                        success = False
                        resp['Error'] = 'Failed to update Fabric Rule DB'
                        logger.error("Failed to delete Rules from fabric Rule DB for Fabric id: " + str(id))
                if not success:
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        To delete a particular fabric
        """
        resp = {}
        fabric = self.get_object(id)
        topology = Topology.objects.get(id=fabric.topology.id)
        topology_json = json.loads(topology.topology_json)
        config_in_fabric = json.loads(fabric.config_json)
        leaf_set = set()
        spine_set = set()
        leaf_set = getSwitch_list(topology_json, LEAF_LIST)
        spine_set = getSwitch_list(topology_json, SPINE_LIST)
        try:
            errmsg, err_bool = update_config_count(config_in_fabric, spine_set, leaf_set, False) 
            if not(err_bool):
                logger.error(errmsg['Error'])
                return Response(errmsg, status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error('Failed to update config_used count')
        try:
            topology.used -= 1
            topology.save()
        except:
            logger.error('Failed to update topology used information' + str(topology.id))
        # deleting discovery rules formed form fabric
        try:
            DiscoveryRule.objects.filter(fabric_id = id).delete()
        except:
            logger.error('Failed to delete discoveryRules with fabric_id: '+str(id))
        try:
            DeployedFabricStats.objects.filter(fabric_id = id).delete()
        except:
            logger.error('Failed to delete Deployed stats with fabric_id: '+str(id))
        if delete_fabric_rules(id):
            fabric.delete()
        else:
            logger.error('Failed to delete Rules from fabric Rule DB for Fabric id: ' + str(id))
        return Response(status=status.HTTP_204_NO_CONTENT)

       
class Profiles(APIView):
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(Profiles, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

            
    def put(self,request,id,format=None):
        
        """
        To update the profiles of fabric
        ---
  serializer: "ProfilesSerializer"

        """
        serializer = ProfilesDictSerializer(data=request.data)
        if serializer.is_valid():    
            resp = {}
            try:
                fabric_obj = Fabric.objects.get(pk=id)
                fabric_obj.profiles = json.dumps(serializer.data)
                fabric_obj.save()
            except:
                resp['Error'] = 'Failed to load profile data for fabric_id: '+str(id)
                logger.error(resp['Error'])
                return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            return JsonResponse(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FabricRuleDBDetail(APIView):
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricRuleDBDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        To fetch the list of Fabric Rules 
        """
        try:
            fabricrule_list = FabricRuleDB.objects.filter(status = True).order_by('id')
        except  FabricRuleDB.DoesNotExist:
            raise Http404
        serializer = FabricRuleDBGetSerializer(fabricrule_list, many=True)
        index = 0
        for item in serializer.data:
            item['fabric_id'] = fabricrule_list[index].fabric.id
            index = index + 1
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Not Allowed
        """
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id, format=None):
        """
        Not Allowed
        """
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, id, format=None):
        """
        Not Allowed
        """
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeployedFabric(APIView):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedFabric, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, format=None):
        """
        To fetch the list of switches deployed form Fabric
        """
        fabric_list = DeployedFabricStats.objects.order_by('fabric_id').distinct('fabric_id').exclude(fabric_id=INVALID)
        data = []
        resp = {}
        for fab in fabric_list:
            try:
                fabric = Fabric.objects.get(id = fab.fabric_id)
            except:
                resp['Error'] = "Fabric not found with id: " + str(fab.fabric_id)
                logger.error(resp['Error'])
                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            fabric_dict = {}
            fabric_dict['fabric_id'] = fab.fabric_id
            if fabric_dict['fabric_id'] != INVALID:
                fabric_dict['fabric_name'] = fabric.name
                replica = DeployedFabricStats.objects.order_by('replica_num').\
                          values_list('replica_num').filter(fabric_id = fab.fabric_id).distinct('replica_num')
                fabric_dict['total_replicas'] = [tuple[0]for tuple in replica]
                data.append(fabric_dict)
            else:
                pass
        serializer = DeployedFabricGetSerializer(data = data, many=True)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class DeployedFabricDetail(APIView):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedFabricDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, fabric_id, replica_num, format=None):
        """
        To get detail of switch deployed by Fabric
        """
        try:
            fabric = Fabric.objects.get(id = fabric_id)
        except:
            logger.error("fabric not found in db with id: " + str(fabric_id))
            raise Http404
        
        try:
            deployed_list = DeployedFabricStats.objects.filter(fabric_id = fabric_id).\
                                                        filter(replica_num = replica_num)
        except:
            logger.error("fabric_id: " +str(fabric_id) + " or replica_num: "+str(replica_num)\
                          + " is not in db:")
            raise Http404
        
        serializer = DeployedFabricDetailGetSerializer(deployed_list, many = True)
        resp = serializer.data
        for stat in resp:
            config = Configuration.objects.get(id = stat['config_id'])
            #stat['config_name'] = config.name
            stat['config_name'] = "View"

        data = {}
        data['fabric_id'] = fabric.id
        data['fabric_name'] = fabric.name
        data['stats'] = resp

        return Response(data)


class DeployedConfig(APIView):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedConfig, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, id, format=None):
        """
        To get deployed switch config file
        """
        try:
            obj = DeployedFabricStats.objects.get(id = id)
        except:
            logger.error("stats not found with id: " + str(id))
            raise Http404
        
        config_full_path = BASE_PATH + obj.configuration_generated

        try:
            wrapper = FileWrapper(file(config_full_path))
        except:
            logger.error("File does not exist with: " + config_full_path)
            raise Http404
        
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(config_full_path)
        return response


class DeployedLogs(APIView):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedLogs, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def preparelogs(self,fName_list,  key1, key2, start_str, end_str, flag):
        sys_fo = ''
        for sysfile in fName_list:
            partial_log_file = []
            if sysfile.endswith('.gz'):
                sys_fo = gzip.open(sysfile,'r')
            else:
                sys_fo = open(sysfile, 'r')
            if sys_fo != '':
                start_string_handler = INVALID
                lines = sys_fo.readlines()
                for index, line in enumerate(lines):
                    words = line.split()
                    try:
                        if flag:
                            if key1 == words[LOG_SEARCH_COL] or key2 == words[LOG_SEARCH_COL]:
                                if start_str in line:
                                    start_string_handler = index
                        else:
                            if start_str in line:
                                start_string_handler = index
                    except:
                        pass
                if start_string_handler != INVALID :
                    for ln in lines[start_string_handler:]:
                        if flag:
                            words = ln.split()
                            if key1 == words[LOG_SEARCH_COL] or key2 == words[LOG_SEARCH_COL]:
                                partial_log_file.append(ln)
                                if end_str in ln:
                                    break
                        else:
                            partial_log_file.append(ln)
                            if end_str in ln:
                                break
            return partial_log_file
        return []
 
    def get(self, request, id, format=None):
        syslog_path = SYSLOG_PATH
        try:
            logs_name = DeployedFabricStats.objects.get(id = id)
        except:
            logger.error("Stats not found with this id: " +str(id))
            resp = {'error':'Logs not found'}
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
        fName_list = getFile_list(syslog_path)
        try:
            if not logs_name.booted :
                loggger.error('log requested for not booted switch '+ logs_name.switch_name)
                return Response([])
            file_with_switch = [REMOTE_SYSLOG_PATH + logs_name.system_id + '.log']
        except:
            file_with_switch = []
        log_file = []
        start_str = POAP_LOG_START
        end_str = POAP_LOG_END
        try:
            log_file += [self.preparelogs(file_with_switch, logs_name.system_id, logs_name.switch_name, start_str, end_str, False)]            
            log_file += [self.preparelogs(fName_list, logs_name.system_id, logs_name.switch_name, start_str, end_str, True)]
            time_list = []
            for item in log_file:
                if len(item):
                    time_list.append(item[0].split()[2])
            try:
                if len(time_list)>1:
                    if time_list[0]>time_list[1]:
                        return Response(log_file[0])
                    else:
                        return Response(log_file[1])
                else:
                    for item in log_file:
                        if len(item):
                            return Response(item)
            except:
                return Response([])
        except:
            resp ={'Error':'Failed to read Syslogs.'}
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        return Response([])

class ImageList(APIView):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ImageList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request,format=None):
        """
        To get list of images
        """
        try:
            serializer = ImagePostSerializer(data = image_objects,many=True)
            if serializer.is_valid():
                img_data = serializer.data
                resp = []
                for image in img_data:
                    img_dtl = {}
                    img_dtl['image_profile_name'] = image['image_profile_name']
                    resp.append(img_dtl)
                return Response(resp)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error('Failed to access image profiles')
            resp = {'Error':'Failed to access image profiles'}
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

class FabricImageEdit(APIView):
   
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricImageEdit, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,id,format=None):
        """
        To update an existing Fabric Image
        ---
  serializer: "ImageDetailSerializer"
        """
        resp = {}
        serializer = ImageDetailSerializer(data = request.data)
        if serializer.is_valid():
            try:
                fabric_obj = Fabric.objects.get(pk=id)
                fabric_obj.image_details = json.dumps(serializer.data)
                fabric_obj.save()
            except:
                resp['Error'] = 'Failed to update Image details for fabric_id: '+str(id)
                return Response(resp, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BuildConfig(APIView):
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(BuildConfig, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, id, format=None):
        error = ""
        fabric_obj = ""
        try:
            fabric_obj = Fabric.objects.get(id=id)
        except:
            error = "Could not find fabric with id %s" %id
            logger.error(error)
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        generate_config(fabric_obj)
        build_fabric_profiles(fabric_obj)   
        return Response("Call to build configs completed",status=status.HTTP_200_OK) 
