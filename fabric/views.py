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
from fabric_rule import generate_fabric_rules, delete_fabric_rules
from serializer.topology_serializer import TopologyGetSerializer, TopologySerializer, TopologyGetDetailSerializer, TopologyPutSerializer
from serializer.fabric_serializer import FabricSerializer, FabricGetSerializer, FabricGetDetailSerializer, FabricPutSerializer
from serializer.fabric_serializer import FabricRuleDBGetSerializer, ImagePostSerializer, ImageDetailSerializer, ProfilesSerializer
from serializer.deployed_serializer import DeployedFabricGetSerializer, DeployedFabricDetailGetSerializer
from configuration.models import Configuration
from discoveryrule.models import DiscoveryRule
from fabric.const import INVALID, LOG_SEARCH_COL
from discoveryrule.models import DiscoveryRule
from discoveryrule.serializer.DiscoveryRuleSerializer import DiscoveryRuleGetDetailSerializer
from fabric.image_profile import image_objects

logger = logging.getLogger(__name__)

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
            
def add_dis_rule(data,success,resp,fabric_id):
    try:
        sys_id_obj = data['system_id']
        config_obj = data['config_json']
        regex  =  data['name'] + '(_)([1-9][0-9]*)(_)([a-zA-Z]*-[1-9])'
        dis_bulk_obj = []
        for switch_systemId_info in sys_id_obj:
            switch_name = (re.search(regex, switch_systemId_info['name'])).group(4)
            replica_num = int((re.search(regex, switch_systemId_info['name'])).group(2))
            system_id = switch_systemId_info['system_id']
            for config in config_obj:
                if switch_name == config['name']:
                    discoveryrule_name = 'serial_'+switch_systemId_info['system_id']
                    
                    dis_rule_obj = DiscoveryRule()
                    dis_rule_obj.priority = 100
                    dis_rule_obj.name = discoveryrule_name
                    dis_rule_obj.config_id = config['configuration_id']
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

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

class TopologyList(APIView):
    """
    Fetch Topology List or Add a new entry to Topology
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(TopologyList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
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
    """
    Retrieve, update or delete a Topology instance.
    """
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
        topology = self.get_object(id)
        count = Fabric.objects.filter(topology = topology).count()
        if count:
            logger.error("Fail to delete Topology id " + str(id) + ", " +\
            str(count) + " Fabrics are using it as base topology")
            return Response("Topology is in use", status=status.HTTP_400_BAD_REQUEST)
        topology.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




class FabricList(APIView):
    """
    Fetch Fabric List or Add a new entry to Fabric
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        fabric_list = Fabric.objects.filter(status = True).order_by('id')
        serializer = FabricGetSerializer(fabric_list, many=True)
        index = 0
        for item in serializer.data:
            item['topology_name'] = fabric_list[index].topology.name
            item['topology_id']  = fabric_list[index].topology.id
            """
            try:
                item['profiles'] = json.loads(data['profiles'])
            except:
                item['profiles'] = {}
            """
            try:
                item['user_name']   = User.objects.get(id=fabric_list[index].user_id).username
            except User.DoesNotExist:
                raise Http404
            index = index + 1
        return Response(serializer.data)

    def post(self, request, format=None):
        
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
                find_dup_data = {'system_id':['system_id','name'], 'config_json':['name']}
                for key,val in find_dup_data.iteritems():
                    for value in val:
                        err_msg, isError = findDuplicate(request.data[key], value)
                        if isError:
                            resp['Error'] = err_msg
                            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
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
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                for config in request.data['config_json']:
                    config_obj = Configuration.objects.get(id = config['configuration_id'])
                    config_obj.used += 1
                    config_obj.save()
                fabric_obj.submit = request.data['submit']
                try:
                    fabric_obj.system_id = json.dumps(request.data['system_id'])
                except:
                    fabric_obj.system_id = []
                """
                try:
                    fabric_obj.profiles = json.dumps(request.data['profiles'])
                except:
                    fabric_obj.profiles = json.dumps({})
                """    
                try:   # fill image details
                    fabric_obj.image_details = json.dumps(request.data['image_details'])
                except:
                    fabric_obj.image_details = json.dumps({})
                try:  # save object
                    fabric_obj.save()
                except:
                    logger.error("Failed to create Fabric: " + fabric_obj.name)
                    resp['Error'] = 'Failed to create Fabric' 
                    return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
                                
                # filling discovery rule with system_id
                success, resp, dis_bulk_obj = add_dis_rule(request.data,success,resp,fabric_obj.id)
                
                if success:   
                    if (generate_fabric_rules(request.data['name'],\
                    request.data['instance'], fabric_obj, request.data['config_json'],\
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
    """
    Retrieve, update or delete a Fabric instance.
    """
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
        topo_detail = {}
        fabric = self.get_object(id)
        serializer = FabricGetDetailSerializer(fabric)
        data = dict(serializer.data)
        data['config_json'] = json.loads(data['config_json'])
        data['system_id'] = json.loads(data['system_id'])
	try:
	    data['image_details'] = json.loads(data['image_details'])
        except:
            data['image_details'] = json.loads("{}")
	"""
        try:
            data['profiles'] = json.loads(data['profiles'])
        except:
            data['profiles'] = {}
        """
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
                find_dup_data = {'system_id':['system_id','name'], 'config_json':['name']}
                for key,val in find_dup_data.iteritems():
                    for value in val:
                        err_msg, isError = findDuplicate(request.data[key], value)
                        if isError:
                            resp['Error'] = err_msg
                            return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                err = uniqueSystenmId(request.data['system_id'], fabric_obj.id)
                if err !="":
                    resp['Error'] = err
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                config_in_fabric = json.loads(fabric_obj.config_json)
                for config in config_in_fabric:
                    config_obj = Configuration.objects.get(id = config['configuration_id'])
                    config_obj.used -= 1
                    config_obj.save()
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                for config in request.data['config_json']:
                    config_obj = Configuration.objects.get(id = config['configuration_id'])
                    config_obj.used += 1
                    config_obj.save()
                fabric_obj.submit = request.data['submit']
                fabric_obj.instance = request.data['instance']
                # filling image details
                try: 
                    fabric_obj.image_details = json.dumps(request.data['image_details'])
                except:
                    pass
                # filling profiles
                """
                try:
                    fabric_obj.profiles = json.loads(request.data['profiles'])
                except:pass
                """
                                # filling discovery rule db
                try:
                    DiscoveryRule.objects.filter(fabric_id=id).delete()
                except:
                    logger.error('Failed to delete Discovery rules with fabric_id:'+str(id))
                    resp['Error'] = ['Failed to delete Discovery rules']
                    return Response(resp, status=status.HTTP_400_BAD_REQUEST)
                success, resp, dis_bulk_obj = add_dis_rule(request.data,success,resp,fabric_obj.id)
                
                if success:
                    if delete_fabric_rules(id):
                        if (generate_fabric_rules(request.data['name'],\
                            request.data['instance'], fabric_obj, request.data['config_json'],\
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
                                data['image_details'] = []
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
        resp = {}
        fabric = self.get_object(id)
        topology = Topology.objects.get(id=fabric.topology.id)
        config_in_fabric = json.loads(fabric.config_json)
        for config in config_in_fabric:
                    config_obj = Configuration.objects.get(id = config['configuration_id'])
                    config_obj.used -= 1
                    config_obj.save()
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
        serializer = ProfilesSerializer(data=request.data)
        if serializer.is_valid():    
            resp = {}
            try:
                fabric_obj = Fabric.objects.get(pk=id)
                fabric_obj.profiles = json.dumps(serializer.data)
                fabric_obj.save()
            except:
                logger.error('Failed to load profile data')
                resp['Error'] = 'Failed to load profile data for fabric_id: '+str(id)
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
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id, format=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    def put(self, request, id, format=None):
        return Response(status=status.HTTP_400_BAD_REQUEST)


class DeployedFabric(APIView):
    """
    GET deployed fabrics
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedFabric, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, format=None):
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
    """
    GET detailed deployed stats
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedFabricDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, fabric_id, replica_num, format=None):
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
            stat['config_name'] = config.name

        data = {}
        data['fabric.id'] = fabric_id
        data['fabric_name'] = fabric.name
        data['stats'] = resp
            
        return Response(data)


class DeployedConfig(APIView):
    """
    GET fabric_stats
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedConfig, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, id, format=None):
        try:
            obj = DeployedFabricStats.objects.get(id = id)
        except:
            logger.error("stats not found with id: " + str(id))
            raise Http404
        
        config_full_path = os.getcwd()+"/repo/"+obj.configuration_generated

        try:
            wrapper = FileWrapper(file(config_full_path))
        except:
            logger.error("File does not exist with: " + config_full_path)
            raise Http404
        
        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(config_full_path)
        return response


class DeployedLogs(APIView):
    """
    GET fabric_stats
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DeployedLogs, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def preparelogs(self,file_obj,  key1, key2):
        partial_log_file = []
        for line in file_obj:
            words = line.split()
            if key1 == words[LOG_SEARCH_COL] or key2 == words[LOG_SEARCH_COL]:
                partial_log_file.append(string.rstrip(line))
        return partial_log_file

    def get(self, request, id, format=None):
        syslog_path = '/var/log/syslog*'
        try:
            logs_name = DeployedFabricStats.objects.get(id = id)
        except:
            logger.error("Stats not found with this id: " +str(id))
            resp = {'error':'Logs not found'}
            return JsonResponse(resp, status=status.HTTP_400_BAD_REQUEST)
        fName_list = getFile_list(syslog_path)
        log_file = []
        for sysfile in fName_list:
            try:
                if sysfile.endswith('.gz'):
                    sys_fh = gzip.open(sysfile,'r')
                    one_log_list= self.preparelogs(sys_fh, logs_name.system_id, logs_name.switch_name)
                    log_file += one_log_list
                else:
                    sys_fh = open(sysfile, 'r')
                    log_file += self.preparelogs(sys_fh, logs_name.system_id, logs_name.switch_name)
            except:
                resp ={'Error':'Failed to read Syslogs.'}
                return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
        return Response(log_file)

class ImageList(APIView):
    """
    GET fabric_stats
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ImageList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request,format=None):
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
    """
    GET fabric_stats
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricImageEdit, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,id,format=None):
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
