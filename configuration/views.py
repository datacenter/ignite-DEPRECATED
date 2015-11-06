__author__  = "Rohit N Dubey"


from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
from models import Configlet,Configuration
import json
from serializer.ConfigletSerializer import ConfigletSerializer, ConfigletGetSerializer
from serializer.ConfigurationSerializer import ConfigurationSerializer, \
    ConfigurationGetSerializer,ConfigurationPutSerializer
from django.http import HttpResponse, Http404
from usermanagement.utils import RequestValidator,parse_file,change_datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import string
import logging
logger = logging.getLogger(__name__)

class ConfigletList(APIView,RequestValidator):
    
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            logger.debug("User Id exist")
            return super(ConfigletList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
            To get the list of configlets
        """
        configlets = Configlet.objects.filter(status = True).order_by('name')
        logger.debug("Total configlets fetched from database: "+str(len(configlets)))
        serializer = ConfigletGetSerializer(configlets, many=True)
        for cfglt_detail in serializer.data:
            try :
                cfglt_detail['parameters'] = json.loads(cfglt_detail['parameters'])
            except:
                logger.error('Unable to find parameters')
        conf = serializer.data
        conf = change_datetime(conf)
        return Response(conf)

    def post(self, request, format=None):
        """
        To add a new configlet
        ---
  serializer: "ConfigletSerializer"

        """
        resp={}
        resp['error']=''
        serializer=ConfigletSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                logger.error('Unable to save while creating new configlet')
                resp['error']='Failed to save the input data'
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ConfigletDetail(APIView,RequestValidator):
    parser_classes = (MultiPartParser, FormParser,)
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ConfigletDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, id):
        try:
            return Configlet.objects.get(pk=id)
        except Configlet.DoesNotExist:
            logger.error("Configlet record not exist for id :"+str(id))
            raise Http404

    def get(self, request, id, format=None):
        """
        To fetch a particular configlet
        """ 
        er={}
        er['error']=''
        configlet = self.get_object(id)
        serializer = ConfigletGetSerializer(configlet)
        try:
            cfglt_detail = serializer.data
            try:
                cfglt_detail['parameters'] = json.loads(cfglt_detail['parameters'])
            except:
                logger.error('Unable to fetch Parameters')
            try:
                cfglt_detail['file'] = []
            except:
                logger.error('unable to fetch file ')
            for line in configlet.config_path.file:
                # remove trailing whitespace/newlines
                cfglt_detail['file'].append(string.rstrip(line))
            return Response(cfglt_detail)
        except:
            er['error']='Failed to fetch the configlet'
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request,id,format=None):
        """
        To upload file for an existing configlet
        ---
  serializer: "ConfigletSerializer"

        """
        resp = {}
        configlet = self.get_object(id)
        configlet.config_path.delete(save=False)
        try:
            file_obj = request.FILES['file']
            configlet.config_path = file_obj
            file_content = file_obj.read()
            params = parse_file(file_content)
            configlet.parameters = json.dumps(params)
            logger.debug("File content: "+str(file_content))
            try:
                configlet.save()
                logger.debug("File named %s saved in db" % (file_obj))
                resp['message'] = "File updated duccessfully."
                serializer = ConfigletSerializer(configlet)
                return Response(serializer.data)
            except:
                resp['error']='Unable to update the configlet '
                logger.error(resp['error'])
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error('Unable to update the configlet with id: '+str(id))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

    def delete(self, request, id, format=None):
        """
        To delete a particular configlet
        """
        er={}
        er['error']=''
        configlet = self.get_object(id)
        try:
            if configlet.used_count==0:
                configlet.delete()
                logger.debug("Configlet record deleted successfully for id :"+str(id))
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                er['error']='This configlet is already in use'
                logger.error(er['error'])
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        except:
            logger.error('Unable to delete configlet with id : '+str(id))
            return Response(status=status.HTTP_204_NO_CONTENT)


def get_user_by_token(tkn):
    try:
        obj = Token.objects.get(pk=tkn)
    except:
        logger.debug("Failed to find token = " + tkn + " in Token table")
        return False, None
    try:
        user = User.objects.get(pk=obj.user_id)
    except:
        logger.debug("Failed to find user = " + str(obj.user_id) + " in Token table")
        return False, None

    logger.debug("User name = " + user.username)

    return True, user

class ConfigurationList(APIView,RequestValidator):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ConfigurationList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        """
        To get the list of configurations
        """
        er={}
        er['error']=''
        configuration = Configuration.objects.filter(status = True).order_by('name')
        serializer = ConfigurationGetSerializer(configuration, many=True)
        index = 0
        try:
            for config_details in serializer.data:
                try:
                    config_details['construct_list'] = json.loads(config_details['construct_list'])
                except:
                    logger.error('Unable to read contruct_list ')
                try:
                    config_details['last_modified_by'] = configuration[index].last_modified_by.username
                except:
                    logger.error('Unable to find username ')
                index += 1
            conf = serializer.data
            conf = change_datetime(conf)
            return Response(conf)
        except:
            er['error']='Unable to get the list of configurations'
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        """
        To add a new Configuration
        ---
  serializer: "ConfigurationSerializer"

        """
        er={}
        er['error']=''
        try:
            tkn = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({'status': 'error','errorCode':'101', 'errorMessage':'Invalid Token'})

        logger.debug("Token = " + tkn)
        ret,user = get_user_by_token(tkn)
        if ret == False:
            return Response({'status': 'error','errorCode':'102', 'errorMessage':'Invalid Token'})
        serializer = ConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                config = json.dumps(serializer.data['construct_list'])
                name = serializer.data['name']
                config_obj = Configuration()
                config_obj.name = name
                config_obj.construct_list = config
                config_obj.last_modified_by = user
                config_obj.submit = serializer.data['submit']
                try:
                    config_obj.save()
                except:
                    logger.error('Failed to save data while creating Configuration')
                for item in serializer.data['construct_list']:
                    configlet_id=item['configlet_id']
                    configlet_object=Configlet.objects.get(id=configlet_id)
                    try:
                        configlet_object.used_count +=1
                        configlet_object.save()
                    except:
                        er['error']='Failed to update configlet count'
                        logger.error(er['error'])
                        return Response(er,status=status.HTTP_400_BAD_REQUEST)
                serializer = ConfigurationGetSerializer(config_obj)
                config_details = serializer.data
                config_details['construct_list'] =  json.loads(config_details['construct_list'])
                return Response(config_details, status=status.HTTP_201_CREATED)
            except:
                er['error']='Unable to create  configuration'
                logger.error("Unable to add a new configuration ")
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConfigurationDetail(APIView,RequestValidator):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ConfigurationDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)


    def get_object(self, id):
        try:
            return Configuration.objects.get(pk=id)
        except Configuration.DoesNotExist:
            logger.error("Configuration record not exist for id :"+str(id))
            raise Http404

    def get(self, request, id, format=None):
        """
        To get a particular Configuration
        """ 
        er={}
        er['error']=''
        configuration = self.get_object(id)
        serializer = ConfigurationGetSerializer(configuration)
        try:
            config_details = serializer.data
            try:
                config_details['construct_list'] =  json.loads(config_details['construct_list'])
            except:
                logger.error('Unable to fetch contruct list for configuration with Id: '+str(id))
            try:
                config_details['last_modified_by'] = configuration.last_modified_by.username
            except:
                logger.error('Unable to get username while fetching configuration for id-'+str(id))
            return Response(config_details)
        except:
            er['error']='Unable to get the requested configuration'
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)
            
    def put(self, request, id, format=None):
        """
        To edit an existing Configuration
        ---
  serializer: "ConfigurationPutSerializer"

        """
        re={}
        re['error']=''
        configuration = self.get_object(id)
        construct_list = json.loads(configuration.construct_list)
        for item in construct_list:
            configlet_id=item['configlet_id']
            configlet_object=Configlet.objects.get(id=configlet_id)
            try:
                configlet_object.used_count -=1
                configlet_object.save()
            except:
                er['error']='Failed to update configlet count'
                logger.error(er['error'])
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        if request.data['name'] == self.get_object(id).name:
            serializer = ConfigurationPutSerializer(data=request.data)
        else:
            serializer = ConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                config_obj =  self.get_object(id)
                config = json.dumps(serializer.data['construct_list'])
                config_obj.name = serializer.data['name']
                config_obj.construct_list = config
                config_obj.submit = serializer.data['submit']
                try:
                    config_obj.save()
                    for item in serializer.data['construct_list']:
                        configlet_id=item['configlet_id']
                        configlet_object=Configlet.objects.get(id=configlet_id)
                        try:
                            configlet_object.used_count +=1
                            configlet_object.save()
                        except:
                            re['error']='Failed to update configlet count'
                            logger.error(er['error'])
                            return Response(er,status=status.HTTP_400_BAD_REQUEST)
                    serializer = ConfigurationGetSerializer(config_obj)
                    resp = serializer.data
                    resp['construct_list'] = json.loads(resp['construct_list'])
                    logger.debug("Configuration record updated successfully for id :"+str(id))
                    return Response(resp)
                except:
                    re['error']='Unable to save update on Configuration'
                    logger.error(er['error'])
                    return Response(er,status=status.HTTP_400_BAD_REQUEST)
            except:
                logger.debug('Data is valid but unable to save data for configuration with Id: '+str(id))
            return Response(resp)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        
    def delete(self, request, id, format=None):
        """
        To delete a configuration
        """
        er={}
        er['error']=''
        configuration = self.get_object(id)
        if configuration.used:
            logger.error("This configuration is being used by some fabric")
            return Response("Configurations is in use", status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                construct_list = json.loads(configuration.construct_list)
                for item in construct_list:
                    configlet_id=item['configlet_id']
                    configlet_object=Configlet.objects.get(id=configlet_id)
                    try:
                        configlet_object.used_count -=1
                        configlet_object.save()
                    except:
                        er['error']='Failed to update configlet count'
                        logger.error(er['error'])
                        return Response(er,status=status.HTTP_400_BAD_REQUEST)
                configuration.delete()
                logger.debug("Configuration record deleted successfully for id :"+str(id))
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                er['error']='Unable to delete configuration'
                logger.error('Unable to delete Configuration with id: '+str(id))
                return Response(er,status=status.HTTP_400_BAD_REQUEST)