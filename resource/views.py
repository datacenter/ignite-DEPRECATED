__author__  = "arunrajms"
from django.db import transaction

from django.shortcuts import render
from rest_framework.views import APIView
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status

import json

from models import Switch

from serializer.SwitchSerializer import SwitchSerializer
from serializer.SwitchSerializer import SwitchGetSerializer

from usermanagement.utils import RequestValidator
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse


class SwitchList(APIView):

    '''
    
    '''
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(SwitchList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            
    def get(self, request, format=None):
        switch = Switch.objects.all()
        serializer = SwitchGetSerializer(switch, many=True)
        return Response(serializer.data)
        

    @transaction.atomic
    def post(self, request, format=None):
        serializer = SwitchSerializer(data=request.data)
        if serializer.is_valid():

            swi_object = Switch()
            swi_object.model = serializer.data['model']
            swi_object.name = serializer.data['name']
            swi_object.image = serializer.data['image']
            swi_object.slots = serializer.data['slots']
            swi_object.tier = serializer.data['tier']
            swi_object.line_cards = str(serializer.data['line_cards'])
            swi_object.save()
            
            serializer = SwitchGetSerializer(swi_object)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class SwitchDetailList(APIView):

    '''
    
    '''
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(SwitchList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
            
            