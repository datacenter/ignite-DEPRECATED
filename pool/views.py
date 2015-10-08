__author__  = "arunrajms"
from django.db import transaction

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
from netaddr import *
import json
import logging

from models import Pool,PoolDetail,PoolFabricDetail
from serializer.PoolSerializer import PoolSerializer
from serializer.PoolSerializer import PoolGetSerializer
from serializer.PoolSerializer import PoolGetDetailSerializer
from serializer.PoolSerializer import PoolPutSerializer


from usermanagement.utils import RequestValidator, change_datetime
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

logger = logging.getLogger(__name__)

class PoolList(APIView):
    """
    List all Pools, or create a new Pools.
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(PoolList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get(self, request, format=None):
        pool = Pool.objects.all()
        serializer = PoolGetSerializer(pool, many=True)
        for single_obj in serializer.data:
            single_obj['range'] =  json.loads(single_obj['range'])
        return Response(serializer.data)
        

    @transaction.atomic
    def post(self, request, format=None):
        serializer = PoolSerializer(data=request.data)
        if serializer.is_valid():

            col_object = Pool()
            col_object.type = serializer.data['type']
            col_object.name = serializer.data['name']
            col_object.scope = serializer.data['scope']
            col_object.save()
            
            type = serializer.data['type']
            coll_range=[{'start':0,'end':1}]
            if type == 'AutoGenerate':
                start = 10
                end = 20
                for flag in range(start,end + 1):
                    coll = PoolDetail()
                    coll.index = col_object
                    coll.value = flag
                    coll.save()
                coll_range[0]['start'] = start
                coll_range[0]['end'] = end
                col_object.range = json.dumps(coll_range)
            else:
                col_object.range = json.dumps(serializer.data['range'])
            col_object.save()

            
            if type == 'Integer' or type =='Vlan':
                for i in range(0,len(serializer.data['range'])):
                    start = int(serializer.data['range'][i]['start'])
                    end = int(serializer.data['range'][i]['end'])
                    for flag in range(start,end + 1):
                        coll = PoolDetail()
                        coll.index = col_object
                        coll.value = flag
                        coll.save()
                    
            if type == 'IP' or type == 'MgmtIP' or type == 'IPv6':
                for i in range(0,len(serializer.data['range'])):
                    start_ip = IPNetwork(str(serializer.data['range'][i]['start']))
                    end_ip = IPNetwork(str(serializer.data['range'][i]['end']))
                    for ip_val in range (start_ip.ip,end_ip.ip+1):
                        coll = PoolDetail()
                        coll.index = col_object
                        coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
                        coll.save()
                    
        
        #    if type == 'IPv6':
        #        start_ip = IPNetwork(str(serializer.data['range'][0]['start']))
        #        end_ip = IPNetwork(str(serializer.data['range'][0]['end']))
        #        for ip_val in range (start_ip.ip,end_ip.ip+1):
        #            coll = PoolDetail()
        #            coll.index = col_object
        #            coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
        #            coll.save()
                    
            get_coll_detail = PoolDetail.objects.filter(index = col_object.id,assigned ='')
            available = len(get_coll_detail)
            col_object.available = available
            col_object.used = len(PoolDetail.objects.filter(index = col_object.id)) - available
            col_object.save()
            serializer = PoolGetSerializer(col_object)
            collect_details = serializer.data
            collect_details['range'] = json.loads(collect_details['range'])
            return Response(collect_details, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class PoolDetailList(APIView):
    '''
    '''
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(PoolDetailList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get_object(self,id):
        try:
            return Pool.objects.get(pk=id)
        except Pool.DoesNotExist:
            raise Http404 
            
           
    def get(self,request,id,format=None):
    
        pool=self.get_object(id)
        serializer=PoolGetSerializer(pool)
        collect_details = serializer.data
        collect_details['range'] = json.loads(collect_details['range'])
        #available_data = PoolDetail.objects.filter(index = id,assigned ='')
        used_data = PoolDetail.objects.filter(index = id).exclude(assigned = '')
        #serializer = PoolGetDetailSerializer(available_data,many=True)
        #collect_details['available_data'] = serializer.data
        serializer = PoolGetDetailSerializer(used_data,many=True)


	collec = serializer.data
	collec = change_datetime(collec)
        collect_details['used_data'] = collec #serializer.data        
        #collect_details['available'] = available_data
        return Response(collect_details)
        
    def put(self,request,id,format=None):
        col_object = self.get_object(id)
        serializer = PoolGetSerializer(col_object)
        collect_details = serializer.data
        collect_details['range'] = json.loads(collect_details['range'])
        
        if request.data['scope'] != self.get_object(id).scope:
            logger.error("Edit for pool failed: Scope change is not allowed")
            return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if request.data['name'] == self.get_object(id).name:
            serializer = PoolPutSerializer(data=request.data)
        else:
            serializer = PoolSerializer(data = request.data)
        
        if serializer.is_valid():
            type = serializer.data['type']
            col_object.name = serializer.data['name']
            
            if type == 'AutoGenerate':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            if type == 'Integer' or type =='Vlan':
                for i in range(0,len(serializer.data['range'])):
                    start = int(serializer.data['range'][i]['start'])
                    end = int(serializer.data['range'][i]['end'])
                    diff = end - start
                
                    for flag in range(start,end + 1):
                        coll = PoolDetail()
                        coll.index = col_object
                        coll.value = flag
                        coll.save()
                    
                    collect_details['range'].append(serializer.data['range'][i])
                    col_object.available = int(col_object.available) + diff + 1
                    
                col_object.range = json.dumps(collect_details['range'])
                col_object.save()
                
                serializer = PoolGetSerializer(col_object)
                collect_details = serializer.data
                collect_details['range'] = json.loads(collect_details['range'])
                return Response(collect_details, status=status.HTTP_206_PARTIAL_CONTENT)
            
            if type =='IP' or type =='MgmtIP' or type =='IPv6':
                for i in range(0,len(serializer.data['range'])):
                    start_ip = IPNetwork(str(serializer.data['range'][0]['start']))
                    end_ip = IPNetwork(str(serializer.data['range'][0]['end']))

                    for ip_val in range (start_ip.ip,end_ip.ip+1):
                        coll = PoolDetail()
                        coll.index = col_object
                        coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
                        coll.save()
                        
                    diff = int(end_ip.ip-start_ip.ip) + 1
                    collect_details['range'].append(serializer.data['range'][i])
                    col_object.available = int(col_object.available) + diff
                    
                col_object.range = json.dumps(collect_details['range'])
                col_object.save()
                serializer = PoolGetSerializer(col_object)
                collect_details = serializer.data
                collect_details['range'] = json.loads(collect_details['range'])
                return Response(collect_details, status=status.HTTP_206_PARTIAL_CONTENT)
           
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,id,format=None):

        pool = self.get_object(id)
        if pool.scope == 'global':
            if pool.used == 0:
                pool.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif pool.scope == 'fabric':
            collec_fab_details = PoolFabricDetail.objects.filter(pool_id=id)
            if collec_fab_details.__len__() == 0:
                pool.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
