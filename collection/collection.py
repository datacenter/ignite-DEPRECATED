__author__  = "arunrajms"

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
import json
import re
import logging

from models import Collection
from models import CollectionDetail
from models import CollectionFabricDetail


from usermanagement.utils import RequestValidator
from django.http import JsonResponse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from pprint import *

logger = logging.getLogger(__name__)

def generate_collection_value(collection_id,fabric_id,switch_name,ifvpc=0):

    logger.debug("Generating Collection with Collection ID: "+str(collection_id)+" Fabric ID: "+str(fabric_id)+" Switch Name: "+str(switch_name))
    collections = Collection.objects.filter(id=collection_id)
    collection = collections.first()
    
    if(collection.scope =='global'):
        logger.debug("Got global collection")
        
        collectiondetails = CollectionDetail.objects.filter(index=collection_id,assigned=str(switch_name))
        
        if (collectiondetails.__len__() == 0 ):
            if(collection.available==0):
                logger.error("Collection is FULL!!!")
                return None
            
            collectiondetails = CollectionDetail.objects.filter(index=collection_id,assigned='')
            collectiondetail = collectiondetails.first()
            collectiondetail.assigned = str(switch_name)
            collectiondetail.save()
            collection.used = collection.used + 1
            collection.available = collection.available-1
            collection.save()
        else:
            logger.debug("Switch name already exists in collection")
            collectiondetail = collectiondetails.first()
            if ifvpc == 0:
                collectiondetail.save()
            
        return collectiondetail.value
        
    elif(collection.scope == 'fabric'):
        
        logger.debug("Got fabric collection")
        collectiondetails = CollectionDetail.objects.filter(index=collection_id)
        collectionfabdetails = CollectionFabricDetail.objects.filter(collec_id=collection_id,assigned=str(switch_name),fab_id=fabric_id)
        col_values = []
        col_used_values = []
        if collectiondetails.__len__() - collectionfabdetails.__len__() == 0:
            logger.error("Exhausted collections")
            return None
            
        for col_det_obj in collectiondetails:
            col_values.append(col_det_obj.value)
            
        if collectionfabdetails.__len__() == 0 :
            #collection.used = collection.used + 1
            collection_value = col_values[0]
        else:
            for col_fab_det_obj in collectionfabdetails:
                col_used_values.append(col_fab_det_obj.value)
                
            col_un_used_values = list(set(col_values)-set(col_used_values))
            col_un_used_values.sort()
            collection_value = col_un_used_values[0]
        
        col_fab_det_obj = CollectionFabricDetail()
        col_fab_det_obj.collec_id = collection
        col_fab_det_obj.value = str(collection_value)
        col_fab_det_obj.fab_id = fabric_id
        col_fab_det_obj.assigned = str(switch_name)
        col_fab_det_obj.save()
        return collection_value
        
        
        

def generate_vpc_peer_dest(fabric_id, switch_name,peer_switch_name):
    logger.debug("Generating VPC peer dest with switch name: "+str(switch_name)+" Peer Switch Name: "+str(peer_switch_name))
    
    collectiondetails = CollectionDetail.objects.filter(assigned=str(switch_name))
    
    for col_det_obj in collectiondetails:
        col_id = col_det_obj.index.id
        #print col_id
        collections = Collection.objects.filter(type='MgmtIP',id=col_id)
        if collections.__len__ != 0 :
            break
    
    return generate_collection_value(col_id, fabric_id, peer_switch_name,1)
        
def delete_collection_value(collection_id,fabric_id,switch_name=100):

    logger.debug("Deleting CollectionDetail with Collection ID: "+str(collection_id)+" Fabric ID: "+str(fabric_id)+" Switch ID: "+str(switch_name))
    collections = Collection.objects.filter(id=collection_id)
    collection = collections.first()
    #print collection.id
    
    if(collection.scope =='global'):
        logger.debug("Got global collection to delete")
        if(collection.available==0):
            return None
        
        collectiondetails = CollectionDetail.objects.filter(index=collection_id,assigned=str(switch_name))
        collectiondetail = collectiondetails.first()
        collectiondetail.assigned = str(switch_name)
        collectiondetail.save()
        collection.used = collection.used + 1
        collection.available = collection.available-1
        collection.save()
        return collectiondetail.value
        #collectiondetails.save()
        #print collectiondetails.values()


def delete_switchid_collection(switch_name):
    logger.debug("Deleting CollectionDetail for Switch ID: "+str(switch_name))
    collections = Collection.objects.filter(scope="global")
    
    for collection_obj in collections:    
        collectiondetails = CollectionDetail.objects.filter(index=collection_obj.id,assigned=str(switch_name))
        for single_obj in collectiondetails.iterator():
            single_obj.assigned=''
            single_obj.save()
            collection_obj.used = collection_obj.used - 1
            collection_obj.available = collection_obj.available + 1
            collection_obj.save()
