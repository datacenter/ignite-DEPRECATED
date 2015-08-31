__author__  = "arunrajms"
from django.db import transaction

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
from netaddr import *
import json

from models import Collection,CollectionDetail,CollectionFabricDetail
from serializer.CollectionSerializer import CollectionSerializer
from serializer.CollectionSerializer import CollectionGetSerializer
from serializer.CollectionSerializer import CollectionGetDetailSerializer
from serializer.CollectionSerializer import CollectionPutSerializer


from usermanagement.utils import RequestValidator, change_datetime
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse


class CollectionList(APIView):
    """
    List all Collections, or create a new Collections.
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(CollectionList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get(self, request, format=None):
        collection = Collection.objects.all()
        serializer = CollectionGetSerializer(collection, many=True)
        for single_obj in serializer.data:
            single_obj['range'] =  json.loads(single_obj['range'])
        return Response(serializer.data)
        

    @transaction.atomic
    def post(self, request, format=None):
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():

            col_object = Collection()
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
                    coll = CollectionDetail()
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
                        coll = CollectionDetail()
                        coll.index = col_object
                        coll.value = flag
                        coll.save()
                    
            if type == 'IP' or type == 'MgmtIP' or type == 'IPv6':
                for i in range(0,len(serializer.data['range'])):
                    start_ip = IPNetwork(str(serializer.data['range'][i]['start']))
                    end_ip = IPNetwork(str(serializer.data['range'][i]['end']))
                    for ip_val in range (start_ip.ip,end_ip.ip+1):
                        coll = CollectionDetail()
                        coll.index = col_object
                        coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
                        coll.save()
                    
        
        #    if type == 'IPv6':
        #        start_ip = IPNetwork(str(serializer.data['range'][0]['start']))
        #        end_ip = IPNetwork(str(serializer.data['range'][0]['end']))
        #        for ip_val in range (start_ip.ip,end_ip.ip+1):
        #            coll = CollectionDetail()
        #            coll.index = col_object
        #            coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
        #            coll.save()
                    
            get_coll_detail = CollectionDetail.objects.filter(index = col_object.id,assigned ='')
            available = len(get_coll_detail)
            col_object.available = available
            col_object.used = len(CollectionDetail.objects.filter(index = col_object.id)) - available
            col_object.save()
            serializer = CollectionGetSerializer(col_object)
            collect_details = serializer.data
            collect_details['range'] = json.loads(collect_details['range'])
            return Response(collect_details, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CollectionDetailList(APIView):
    '''
    '''
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(CollectionDetailList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get_object(self,id):
        try:
            return Collection.objects.get(pk=id)
        except Collection.DoesNotExist:
            raise Http404 
            
           
    def get(self,request,id,format=None):
    
        collection=self.get_object(id)
        serializer=CollectionGetSerializer(collection)
        collect_details = serializer.data
        collect_details['range'] = json.loads(collect_details['range'])
        #available_data = CollectionDetail.objects.filter(index = id,assigned ='')
        used_data = CollectionDetail.objects.filter(index = id).exclude(assigned = '')
        #serializer = CollectionGetDetailSerializer(available_data,many=True)
        #collect_details['available_data'] = serializer.data
        serializer = CollectionGetDetailSerializer(used_data,many=True)


	collec = serializer.data
	collec = change_datetime(collec)
        collect_details['used_data'] = collec #serializer.data        
        #collect_details['available'] = available_data
        return Response(collect_details)
        
    def put(self,request,id,format=None):
        col_object = self.get_object(id)
        serializer = CollectionGetSerializer(col_object)
        collect_details = serializer.data
        collect_details['range'] = json.loads(collect_details['range'])
        serializer = CollectionPutSerializer(data=request.data)
        
        if serializer.is_valid():
            type = serializer.data['type']
            
            if type == 'AutoGenerate':
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            if type == 'Integer' or type =='Vlan':
                for i in range(0,len(serializer.data['range'])):
                    start = int(serializer.data['range'][i]['start'])
                    end = int(serializer.data['range'][i]['end'])
                    diff = end - start
                
                    for flag in range(start,end + 1):
                        coll = CollectionDetail()
                        coll.index = col_object
                        coll.value = flag
                        coll.save()
                    
                    collect_details['range'].append(serializer.data['range'][i])
                    col_object.available = int(col_object.available) + diff + 1
                    
                col_object.range = json.dumps(collect_details['range'])
                col_object.save()
                
                serializer = CollectionGetSerializer(col_object)
                collect_details = serializer.data
                collect_details['range'] = json.loads(collect_details['range'])
                return Response(collect_details, status=status.HTTP_206_PARTIAL_CONTENT)
            
            if type =='IP' or type =='MgmtIP' or type =='IPv6':
                for i in range(0,len(serializer.data['range'])):
                    start_ip = IPNetwork(str(serializer.data['range'][0]['start']))
                    end_ip = IPNetwork(str(serializer.data['range'][0]['end']))

                    for ip_val in range (start_ip.ip,end_ip.ip+1):
                        coll = CollectionDetail()
                        coll.index = col_object
                        coll.value = IPAddress(ip_val).__str__()+"/"+start_ip.prefixlen.__str__()
                        coll.save()
                        
                    diff = int(end_ip.ip-start_ip.ip) + 1
                    collect_details['range'].append(serializer.data['range'][i])
                    col_object.available = int(col_object.available) + diff
                    
                col_object.range = json.dumps(collect_details['range'])
                col_object.save()
                serializer = CollectionGetSerializer(col_object)
                collect_details = serializer.data
                collect_details['range'] = json.loads(collect_details['range'])
                return Response(collect_details, status=status.HTTP_206_PARTIAL_CONTENT)
               
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self,request,id,format=None):

        collection = self.get_object(id)
        if collection.scope == 'global':
            if collection.used == 0:
                collection.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif collection.scope == 'fabric':
            collec_fab_details = CollectionFabricDetail.objects.filter(collec_id=id)
            if collec_fab_details.__len__() == 0:
                collection.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
