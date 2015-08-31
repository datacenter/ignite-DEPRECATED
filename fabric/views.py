from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404, JsonResponse
from usermanagement.utils import RequestValidator
from django.contrib.auth.models import User
import json
import logging
import pprint
#Imports from user defined modules
from models import Topology, Fabric, FabricRuleDB
from fabric_rule import generate_fabric_rules, delete_fabric_rules
from serializer.topology_serializer import TopologyGetSerializer, TopologySerializer, TopologyGetDetailSerializer, TopologyPutSerializer
from serializer.fabric_serializer import FabricSerializer, FabricGetSerializer, FabricGetDetailSerializer, FabricPutSerializer
from serializer.fabric_serializer import FabricRuleDBGetSerializer

logger = logging.getLogger(__name__)

# Create your views here.
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
                topology_obj.save()
                serailizer = TopologyGetDetailSerializer(topology_obj)
                resp = serailizer.data
                resp['topology_json'] = json.loads(resp['topology_json'])
                try:
                    resp['config_json'] = json.loads(resp['config_json'])
                except:
                    resp['config_json'] = []
                return Response(resp)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        topology = self.get_object(id)
        count = Fabric.objects.filter(topology = topology).count()
        if count:
            logger.error("Fail to delete Topology id " + str(id) + ", " +\
            str(count) + " Fabrics are using it as base topology")
            return Response(status=status.HTTP_400_BAD_REQUEST)
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
            try:
                item['user_name']   = User.objects.get(id=fabric_list[index].user_id).username
            except User.DoesNotExist:
                raise Http404
            index = index + 1
        return Response(serializer.data)

    def post(self, request, format=None):

        serializer = FabricSerializer(data=request.data)
        topology = Topology.objects.get(id=request.data['topology_id'])
        topology_json = json.loads(topology.topology_json)
        me = RequestValidator(request.META)
        if serializer.is_valid():
            if request.data['instance'] < 1:
                logger.error("Fabric Instances cannot be less than 1")
            else:
                fabric_obj = Fabric()
                fabric_obj.name = request.data['name']
                fabric_obj.user_id = me.user_is_exist().user_id
                fabric_obj.topology = topology
                topology.used += 1
                topology.save()
                fabric_obj.instance = request.data['instance']
                fabric_obj.validate = request.data['validate']
                fabric_obj.locked = request.data['locked']
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                fabric_obj.submit = request.data['submit']
                fabric_obj.save()
                if (generate_fabric_rules(request.data['name'],\
                request.data['instance'], fabric_obj, request.data['config_json'],\
                topology_json)):
                    serializer = FabricGetSerializer(fabric_obj)
                    logger.info("Successfully created Fabric id: " + str(id))
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                else:
                    Fabric.objects.filter(id = fabric_obj.id).delete()
                    logger.error("Failed to create Fabric: " + fabric_obj.name)
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
                fabric_obj.config_json = json.dumps(request.data['config_json'])
                fabric_obj.submit = request.data['submit']
                fabric_obj.instance = request.data['instance']
                if delete_fabric_rules(id):
                    if (generate_fabric_rules(request.data['name'],\
                        request.data['instance'], fabric_obj, request.data['config_json'],\
                        topology_json)):
                        logger.error("Failed to update Fabric id: " + str(id))
                        logger.info("Successfully  update Fabric id: " + str(id))
                        serializer = FabricGetDetailSerializer(fabric_obj)
                        resp = serializer.data
                        resp['config_json'] = json.loads(resp['config_json'])
                        fabric_obj.save()
                        return Response(resp)
                    else:
                        logger.error("Failed to update Fabric id: " + str(id))
                else:
                    logger.error("Failed to delete Rules from fabric Rule DB for Fabric id: " + str(id))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        fabric = self.get_object(id)
        topology = Topology.objects.get(id=fabric.topology.id)
        try:
            topology.used -= 1
            topology.save()
        except:
            logger.error("Failed to update topology used information" + str(topology.id))
        if delete_fabric_rules(id):
            fabric.delete()
        else:
            logger.error("Failed to delete Rules from fabric Rule DB for Fabric id: " + str(id))
        return Response(status=status.HTTP_204_NO_CONTENT)


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

