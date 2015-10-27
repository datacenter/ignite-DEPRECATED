from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import os
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
from models import FabricProfile, ProfileTemplate
import json
from fabric_profile.serializer.FabricProfileSerializer import FabricProfileSerializer,\
                         FabricProfileGetSerializer, FabricProfilePutSerializer, ProfileTemplateSerializer, ProfileTemplateGetSerializer
from django.http import HttpResponse, Http404
from usermanagement.utils import RequestValidator,parse_file,change_datetime
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import string
import logging

logger = logging.getLogger(__name__)

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

"""
Profile template
"""
class ProfileTemplateList(APIView,RequestValidator):
    """
    List all Profile Templates, or create a new Profile Teamplate.
    """

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            logger.debug("User Id exist")
            return super(ProfileTemplateList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        
        ProfileTemplates = ProfileTemplate.objects.filter(status=True).order_by('name')
        logger.debug("Total Profile Templates fetched from database: "+str(len(ProfileTemplates)))
        serializer=ProfileTemplateGetSerializer(ProfileTemplates, many=True)
        for pr_temp_detail in serializer.data:
            try :
                pr_temp_detail['parameters'] = json.loads(pr_temp_detail['parameters'])
            except:
                pass
        proT = serializer.data
        proT = change_datetime(proT)
        return Response(proT)
    
    def post(self, request, format=None):
        serializer=ProfileTemplateSerializer(data=request.data)
        if serializer.is_valid():
            logger.debug("Json input for create Profile Template is valid")
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.warning("Json input for create Profile Template is invalid")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    
class ProfileTemplateDetail(APIView,RequestValidator):

    """
    Retrieve, update or delete a Profile template  instance.
    """
    parser_classes = (MultiPartParser, FormParser,)


    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ProfileTemplateDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, id):
        try:
            return ProfileTemplate.objects.get(pk=id)
        except ProfileTemplate.DoesNotExist:
            logger.error("ProfileTemplate record not exist for id :"+str(id))

            raise Http404
    
    def get(self, request, id, format=None):
        
        ProfileTemplate=self.get_object(id)
        serializer = ProfileTemplateGetSerializer(ProfileTemplate)
        pr_temp_detail = serializer.data
        pr_temp_detail['parameters'] = json.loads(pr_temp_detail['parameters'])
        pr_temp_detail['file'] = []
        for line in ProfileTemplate.config_path.file:
            # remove trailing whitespace/newlines
            pr_temp_detail['file'].append(string.rstrip(line))

        return Response(pr_temp_detail)
    
    def put(self, request, id, format=None):
        ProfileTemplate=self.get_object(id)
        ProfileTemplate.config_path.delete(save=False)
        file_obj = request.FILES['file']
        ProfileTemplate.config_path = file_obj
        file_content = file_obj.read()
        params = parse_file(file_content)
        ProfileTemplate.parameters = json.dumps(params)
        logger.debug("File content: "+str(file_content))
        ProfileTemplate.save()
        logger.debug("File named %s saved in db" % (file_obj))
        resp = {}
        resp['message'] = "File updated successfully."
        serializer = ProfileTemplateSerializer(ProfileTemplate)
        return Response(serializer.data)
    
    def delete(self, request, id, format=None):
        ProfileTemplate = self.get_object(id)
        ProfileTemplate.delete()
        logger.debug("Profile Template record deleted successfully for id :"+str(id))
        return Response(status=status.HTTP_204_NO_CONTENT)

"""
FabricProfile
"""

class FabricProfileList(APIView,RequestValidator):
    """
    List all FabricProfile, or create a new FabricProfile.
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricProfileList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        FabricProfiles = FabricProfile.objects.filter(status = True).order_by('name')
        serializer = FabricProfileGetSerializer(FabricProfiles, many=True)
        index = 0
        for fab_pro_details in serializer.data:
            try:
                del(fab_pro_details['construct_list'])
                fab_pro_details['last_modified_by'] = FabricProfiles[index].last_modified_by.username
            except:
                logger.error('Failed to update')
            index += 1
        fabp = serializer.data
        fabp = change_datetime(fabp)

        return Response(fabp)

    def post(self, request, format=None):
        try:
            tkn = request.META["HTTP_AUTHORIZATION"]
        except:
            return Response({'status': 'error','errorCode':'101', 'errorMessage':'Invalid Token'})

        logger.debug("Token = " + tkn)
        ret,user = get_user_by_token(tkn)
        if ret == False:
            return Response({'status': 'error','errorCode':'102', 'errorMessage':'Invalid Token'})

        serializer = FabricProfileSerializer(data=request.data)
        if serializer.is_valid():
            fabp = json.dumps(serializer.data['construct_list'])
            name = serializer.data['name']
            fabp_obj = FabricProfile()
            fabp_obj.name = name
            fabp_obj.construct_list = fabp
            fabp_obj.last_modified_by = user
            fabp_obj.submit = serializer.data['submit']
            fabp_obj.save()
            logger.debug("FabricProfile created successfully")
            serializer = FabricProfileGetSerializer(fabp_obj)
            fab_pro_details = serializer.data
            fab_pro_details['construct_list'] =  json.loads(fab_pro_details['construct_list'])
            return Response(fab_pro_details, status=status.HTTP_201_CREATED)
        logger.error("Invalid Json  ")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FabricProfileDetail(APIView,RequestValidator):

    """
    Retrieve, update or delete a FabricProfile  instance.
    """
    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricProfileDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)


    def get_object(self, id):
        try:
            return FabricProfile.objects.get(pk=id)
        except FabricProfile.DoesNotExist:
            logger.error("FabricProfile record not exist for id :"+str(id))
            raise Http404

    def get(self, request, id, format=None):
        FabricProfile = self.get_object(id)
        serializer = FabricProfileGetSerializer(FabricProfile)
        fab_pro_details = serializer.data
        fab_pro_details['construct_list'] =  json.loads(fab_pro_details['construct_list'])
        fab_pro_details['last_modified_by'] = FabricProfile.last_modified_by.username
        return Response(fab_pro_details)

    def put(self, request, id, format=None):
        FabricProfile = self.get_object(id)
        if request.data['name'] == self.get_object(id).name:
            serializer = FabricProfilePutSerializer(data=request.data)
        else:
            serializer = FabricProfileSerializer(data=request.data)
        if serializer.is_valid():
            fabp_obj =  self.get_object(id)
            fabp = json.dumps(serializer.data['construct_list'])
            fabp_obj.name = serializer.data['name']
            fabp_obj.construct_list = fabp
            fabp_obj.submit = serializer.data['submit']
            fabp_obj.save()
            serializer = FabricProfileGetSerializer(fabp_obj)
            resp = serializer.data
            resp['construct_list'] = json.loads(resp['construct_list'])
            logger.debug("FabricProfile record updated successfully for id :"+str(id))
            return Response(resp)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        FabricProfile = self.get_object(id)
        if FabricProfile.used:
            logger.error("This FabricProfile is being used by some fabric")
            return Response("FabricProfiles is in use", status=status.HTTP_400_BAD_REQUEST)
        else:
            FabricProfile.delete()
            logger.debug("FabricProfile record deleted successfully for id :"+str(id))
            return Response(status=status.HTTP_204_NO_CONTENT)
