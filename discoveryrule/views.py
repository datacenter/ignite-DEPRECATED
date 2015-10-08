__author__  = "arunrajms"

from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
import ast
import random
import json
import logging
logger = logging.getLogger(__name__)

from models import DiscoveryRule
from serializer.DiscoveryRuleSerializer import DiscoveryRuleSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleGetSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleGetDetailSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleSerialIDSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRulePutSerializer
from serializer.DiscoveryRuleSerializer import DiscoveryRuleIDPutSerializer

from usermanagement.utils import RequestValidator
from django.http import JsonResponse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt


class DiscoveryRuleList(APIView,RequestValidator):
    """
    List all DiscoveryRule, or create a new Rule.
    """
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DiscoveryRuleList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
    def get(self, request, format=None):
        discoveryrule = DiscoveryRule.objects.all()
        serializer = DiscoveryRuleGetSerializer(discoveryrule, many=True)
        index = 0
        resp = []
        for item in serializer.data:
            try:
                if item['fabric_id'] == -1:
                    item['user_name'] = User.objects.get(id=discoveryrule[index].user_id).username
                    del item['fabric_id']
                    resp.append(item)
            except User.DoesNotExist:
                #TODO : log
                logger.error("Username does not exist")
                raise Http404
            index = index + 1
        return Response(resp)

    def post(self, request, format=None):
        me = RequestValidator(request.META)
        if request.data['match']!='serial_id':
            serializer = DiscoveryRuleSerializer(data=request.data)
            if serializer.is_valid():
                rule_object = DiscoveryRule()
                rule_object.name = serializer.data['name']
                rule_object.priority = serializer.data['priority']
                rule_object.user_id = me.user_is_exist().user_id
                rule_object.config_id = serializer.data['config_id']
                rule_object.subrules = json.dumps(serializer.data['subrules'])
                rule_object.match = serializer.data['match'].lower()
                rule_object.save()
                serializer = DiscoveryRuleGetSerializer(rule_object)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            serializer = DiscoveryRuleSerialIDSerializer(data=request.data)
            if serializer.is_valid():
                rule_object = DiscoveryRule()
                rule_object.name = serializer.data['name']
                rule_object.priority = serializer.data['priority']
                rule_object.user_id = me.user_is_exist().user_id
                rule_object.config_id = serializer.data['config_id']
                for i in range(len(serializer.data['subrules'])):
                    serializer.data['subrules'][i]=str(serializer.data['subrules'][i])
                rule_object.subrules = str(serializer.data['subrules'])
                rule_object.match = serializer.data['match']
                rule_object.save()
                serializer = DiscoveryRuleGetSerializer(rule_object)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class DiscoveryRuleDetailList(APIView,RequestValidator):
    '''
    '''
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(DiscoveryRuleDetailList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get_object(self,id):
        try:
            return DiscoveryRule.objects.get(pk=id)
        except DiscoveryRule.DoesNotExist:
            raise Http404 
           
    def get(self,request,id,format=None):
        discoveryrule=self.get_object(id)
        serializer1 = DiscoveryRuleGetSerializer(discoveryrule)
        if serializer1.data['match']!='serial_id':
            serializer = DiscoveryRuleGetDetailSerializer(discoveryrule)
            data = dict(serializer.data)
            data['subrules'] = json.loads(data['subrules'])
            data['user_name'] = User.objects.get(id=discoveryrule.user_id).username
            return Response(data)
        else:
            data = dict(serializer1.data)
            data['subrules'] = ast.literal_eval(str(discoveryrule.subrules))
            data['user_name'] = User.objects.get(id=discoveryrule.user_id).username
            return Response(data)
        
    def put(self, request, id, format=None):
        me = RequestValidator(request.META)
        discoveryrule=self.get_object(id)
        if request.data['match']!='serial_id':
            if request.data['name'] == self.get_object(id).name:
                serializer = DiscoveryRulePutSerializer(data=request.data)
            else:
                serializer = DiscoveryRuleSerializer(data=request.data)
            if serializer.is_valid():
                rule_object = self.get_object(id)
                subrules = json.dumps(serializer.data['subrules'])
                rule_object.name = serializer.data['name']
                rule_object.subrules = subrules
                rule_object.priority = serializer.data['priority']
                rule_object.user_id = me.user_is_exist().user_id
                rule_object.config_id = serializer.data['config_id'] 
                rule_object.match = serializer.data['match'].lower()
                rule_object.save()
                serializer = DiscoveryRuleGetDetailSerializer(rule_object)
                resp = serializer.data
                resp['subrules'] = json.loads(resp['subrules'])
                return Response(resp)
        else:
            if request.data['name'] == self.get_object(id).name:
                serializer = DiscoveryRuleIDPutSerializer(data=request.data)
            else:
                serializer = DiscoveryRuleSerialIDSerializer(data=request.data)
            if serializer.is_valid():
                rule_object = self.get_object(id)
                for i in range(len(serializer.data['subrules'])):
                    serializer.data['subrules'][i]=str(serializer.data['subrules'][i])
                subrules = str(serializer.data['subrules'])
                rule_object.name = serializer.data['name']
                rule_object.subrules = subrules
                rule_object.priority = serializer.data['priority']
                rule_object.user_id = me.user_is_exist().user_id
                rule_object.config_id = serializer.data['config_id'] 
                rule_object.match = serializer.data['match'].lower()
                rule_object.save()
                return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id,format=None):
        discoveryrule = self.get_object(id)
        discoveryrule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
