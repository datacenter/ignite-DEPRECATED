__author__  = "arunrajms"

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
import json
import re
import logging

from models import Pool
from models import PoolDetail
from models import PoolFabricDetail


from usermanagement.utils import RequestValidator
from django.http import JsonResponse
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from pprint import *

logger = logging.getLogger(__name__)

def generate_pool_value(pool_id,fabric_id,switch_name,ifvpc=0):

    logger.debug("Generating Pool with Pool ID: "+str(pool_id)+" Fabric ID: "+str(fabric_id)+" Switch Name: "+str(switch_name))
    pools = Pool.objects.filter(id=pool_id)
    pool = pools.first()
    
    if(pool.scope =='global'):
        logger.debug("Got global pool")
        
        pooldetails = PoolDetail.objects.filter(index=pool_id,assigned=str(switch_name))
        
        if (pooldetails.__len__() == 0 ):
            if(pool.available==0):
                logger.error("Pool is FULL!!!")
                return None
            
            pooldetails = PoolDetail.objects.filter(index=pool_id,assigned='')
            pooldetail = pooldetails.first()
            pooldetail.assigned = str(switch_name)
            pooldetail.save()
            pool.used = pool.used + 1
            pool.available = pool.available-1
            pool.save()
        else:
            logger.debug("Switch name already exists in pool")
            pooldetail = pooldetails.first()
            if ifvpc == 0:
                pooldetail.save()
            
        return pooldetail.value
        
    elif(pool.scope == 'fabric'):
        
        logger.debug("Got fabric pool")
        pooldetails = PoolDetail.objects.filter(index=pool_id)
        poolfabdetails = PoolFabricDetail.objects.filter(pool_id=pool_id,assigned=str(switch_name),fab_id=fabric_id)
        pool_values = []
        pool_used_values = []
        if pooldetails.__len__() - poolfabdetails.__len__() == 0:
            logger.error("Exhausted pools")
            return None
            
        for pool_det_obj in pooldetails:
            pool_values.append(pool_det_obj.value)
            
        if poolfabdetails.__len__() == 0 :
            #pool.used = pool.used + 1
            pool_value = pool_values[0]
        else:
            for pool_fab_det_obj in poolfabdetails:
                pool_used_values.append(pool_fab_det_obj.value)
                
            pool_un_used_values = list(set(pool_values)-set(pool_used_values))
            pool_un_used_values.sort()
            pool_value = pool_un_used_values[0]
        
        pool_fab_det_obj = PoolFabricDetail()
        pool_fab_det_obj.pool_id = pool
        pool_fab_det_obj.value = str(pool_value)
        pool_fab_det_obj.fab_id = fabric_id
        pool_fab_det_obj.assigned = str(switch_name)
        pool_fab_det_obj.save()
        return pool_value
        
        
        

def generate_vpc_peer_dest(fabric_id, switch_name,peer_switch_name):
    logger.debug("Generating VPC peer dest with switch name: "+str(switch_name)+" Peer Switch Name: "+str(peer_switch_name))
    
    pooldetails = PoolDetail.objects.filter(assigned=str(switch_name))
    
    for pool_det_obj in pooldetails:
        pool_id = pool_det_obj.index.id
        #print pool_id
        pools = Pool.objects.filter(type='MgmtIP',id=pool_id)
        if pools.__len__ != 0 :
            break
    
    return generate_pool_value(pool_id, fabric_id, peer_switch_name,1)
        
def delete_pool_value(pool_id,fabric_id,switch_name=100):

    logger.debug("Deleting PoolDetail with Pool ID: "+str(pool_id)+" Fabric ID: "+str(fabric_id)+" Switch ID: "+str(switch_name))
    pools = Pool.objects.filter(id=pool_id)
    pool = pools.first()
    #print pool.id
    
    if(pool.scope =='global'):
        logger.debug("Got global pool to delete")
        if(pool.available==0):
            return None
        
        pooldetails = PoolDetail.objects.filter(index=pool_id,assigned=str(switch_name))
        pooldetail = pooldetails.first()
        pooldetail.assigned = str(switch_name)
        pooldetail.save()
        pool.used = pool.used + 1
        pool.available = pool.available-1
        pool.save()
        return pooldetail.value
        #pooldetails.save()
        #print pooldetails.values()


def delete_switchid_pool(switch_name):
    logger.debug("Deleting PoolDetail for Switch ID: "+str(switch_name))
    pools = Pool.objects.filter(scope="global")
    
    for pool_obj in pools:    
        pooldetails = PoolDetail.objects.filter(index=pool_obj.id,assigned=str(switch_name))
        for single_obj in pooldetails.iterator():
            single_obj.assigned=''
            single_obj.save()
            pool_obj.used = pool_obj.used - 1
            pool_obj.available = pool_obj.available + 1
            pool_obj.save()
