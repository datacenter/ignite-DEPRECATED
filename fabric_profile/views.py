from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
import os
import sys
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
 
class ProfileTemplateList(APIView,RequestValidator):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            logger.debug("User Id exist")
            return super(ProfileTemplateList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, format=None):
        """
        To fetch all profile templates
        """ 
        ProfileTemplates = ProfileTemplate.objects.filter(status=True).order_by('name')
        logger.debug("Total Profile Templates fetched from database: "+str(len(ProfileTemplates)))
        serializer=ProfileTemplateGetSerializer(ProfileTemplates, many=True)
        for pr_temp_detail in serializer.data:
            try :
                pr_temp_detail['parameters'] = json.loads(pr_temp_detail['parameters'])
            except:
                logger.error('Unable to fetch parameters')
        proT = serializer.data
        proT = change_datetime(proT)
        return Response(proT)
    
    def post(self, request, format=None):
        """
        To create a new profile template
        ---
  serializer: "ProfileTemplateSerializer"

        """
        resp={}
        resp['error']=''
        serializer=ProfileTemplateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except:
                logger.error('Unable to save while creating new profile template')
                resp['error']='Failed to save the input data'
                return Response(resp,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 
    
    
class ProfileTemplateDetail(APIView,RequestValidator):

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
        """
        To fetch a particular Profile Template
        """
        ProfileTemplate=self.get_object(id)
        serializer = ProfileTemplateGetSerializer(ProfileTemplate)
        try:
            pr_temp_detail = serializer.data
            try:
                pr_temp_detail['parameters'] = json.loads(pr_temp_detail['parameters'])
            except:
                logger.error('Unable to get parameters of Profile Template with Id: '+str(id))
            pr_temp_detail['file'] = []
            try:
                for line in ProfileTemplate.config_path.file:
                    # remove trailing whitespace/newlines
                    pr_temp_detail['file'].append(string.rstrip(line))
            except:
                logger.error('Unable to fetch file to list profile template')
            return Response(pr_temp_detail)
        except:
            logger.error('Unable to fetch Profile Template')
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, id, format=None):
        """
        To update an existing Profile template
        ---
  serializer: "ProfileTemplateSerializer"

        """
        er={}
        er['error']=''
        ProfileTemplate=self.get_object(id)
        ProfileTemplate.config_path.delete(save=False)
        try:
            file_obj = request.FILES['file']
            ProfileTemplate.config_path = file_obj
            file_content = file_obj.read()
            params = parse_file(file_content)
            ProfileTemplate.parameters = json.dumps(params)
            logger.debug("File content: "+str(file_content))
            try:
                ProfileTemplate.save()
                logger.debug("File named %s saved in db" % (file_obj))
                resp = {}
                resp['message'] = "File updated successfully."
                serializer = ProfileTemplateSerializer(ProfileTemplate)
                return Response(serializer.data)
            except:
                er['error']='Unable to save file to db'
                logger.error(er['error'])
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        except:
            er['error']='Unable to update profile template'
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request, id, format=None):
        """
        To delete a profile Template
        """
        er={}
        er['error']=''
        ProfileTemplate = self.get_object(id)
        try:
            if ProfileTemplate.used_count==0:
                ProfileTemplate.delete()
                logger.debug("Profile Template record deleted successfully for id :"+str(id))
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                er['error']='This profile template is already in use'
                logger.error(er['error'])
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        except:
            er['error']='Unable to delete Profile template'
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)

class FabricProfileList(APIView,RequestValidator):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(FabricProfileList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        To fetch the list of Fabric profiles
        """
        FabricProfiles = FabricProfile.objects.filter(status = True).order_by('name')
        serializer = FabricProfileGetSerializer(FabricProfiles, many=True)
        index = 0
        for fab_pro_details in serializer.data:
            try:
                del(fab_pro_details['construct_list'])
                fab_pro_details['last_modified_by'] = FabricProfiles[index].last_modified_by.username
            except:
                logger.error('Failed to update data')
            index += 1
        fabp = serializer.data
        fabp = change_datetime(fabp)

        return Response(fabp)

    def post(self, request, format=None):
        """
        To create a new Fabric Profile
        ---
  serializer: "FabricProfileSerializer"

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
        serializer = FabricProfileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                fabp = json.dumps(serializer.data['construct_list'])
                name = serializer.data['name']
                fabp_obj = FabricProfile()
                fabp_obj.name = name
                fabp_obj.construct_list = fabp
                fabp_obj.last_modified_by = user
                try:
                    fabp_obj.submit = serializer.data['submit']
                except:
                    logger.error('Unable to submit Fabric profile')
                try:
                    fabp_obj.save()
                    logger.debug("FabricProfile created successfully")
                except:
                    logger.error('Unable to create fabric profile- Save operation failed')
                for item in serializer.data['construct_list']:
                    profile_template_id=item['template_id']
                    profile_template_object=ProfileTemplate.objects.get(id=profile_template_id)
                    try:
                        profile_template_object.used_count +=1
                        profile_template_object.save()
                    except:
                        er['error']='Failed to update profile template count'
                        logger.error(er['error'])
                        return Response(er,status=status.HTTP_400_BAD_REQUEST)
                serializer = FabricProfileGetSerializer(fabp_obj)
                fab_pro_details = serializer.data
                fab_pro_details['construct_list'] =  json.loads(fab_pro_details['construct_list'])
                return Response(fab_pro_details, status=status.HTTP_201_CREATED)
            except:
                er['error']='Unable to get data'
                logger.error('Unable to get data ')
                return Response (er,status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FabricProfileDetail(APIView,RequestValidator):

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
        """
        To fetch a Fabric Profile
        """
        er={}
        er['error']=''
        FabricProfile = self.get_object(id)
        serializer = FabricProfileGetSerializer(FabricProfile)
        try:
            fab_pro_details = serializer.data
            try:
                fab_pro_details['construct_list'] =  json.loads(fab_pro_details['construct_list'])
            except:
                loger.error('Unable to get construct list in listing the Fabric profile with id :'+str(id))
            try:
                fab_pro_details['last_modified_by'] = FabricProfile.last_modified_by.username
            except:
                logger.error('Unable to find Username')
            return Response(fab_pro_details)
        except:
            er['error']='Unable to fetch the fabric profile '
            logger.error(er['error'])
            return Response(er,status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id, format=None):
        """
        To update an exiting Fabric Profile
        ---
  serializer: "FabricProfileSerializer"

        """
        re={}
        re['error']=''
        FabricProfile = self.get_object(id)
        construct_list = json.loads(FabricProfile.construct_list)
        for item in construct_list:
            profile_template_id=item['template_id']
            profile_template_object=ProfileTemplate.objects.get(id=profile_template_id)
            try:
                profile_template_object.used_count -=1
                profile_template_object.save()
            except:
                er['error']='Failed to update profile template count'
                logger.error(er['error'])
                return Response(er,status=status.HTTP_400_BAD_REQUEST)
        if request.data['name'] == self.get_object(id).name:
            serializer = FabricProfilePutSerializer(data=request.data)
        else:
            serializer = FabricProfileSerializer(data=request.data)
        if serializer.is_valid():
            try:
                fabp_obj =  self.get_object(id)
                fabp = json.dumps(serializer.data['construct_list'])
                fabp_obj.name = serializer.data['name']
                fabp_obj.construct_list = fabp
                fabp_obj.submit = serializer.data['submit']
                try:
                    fabp_obj.save()
                    for item in serializer.data['construct_list']:
                        profile_template_id=item['template_id']
                        profile_template_object=ProfileTemplate.objects.get(id=profile_template_id)
                        try:
                            profile_template_object.used_count +=1
                            profile_template_object.save()
                        except:
                            er['error']='Failed to update profile template count'
                            logger.error(er['error'])
                            return Response(er,status=status.HTTP_400_BAD_REQUEST)
                    serializer = FabricProfileGetSerializer(fabp_obj)
                    resp = serializer.data
                    resp['construct_list'] = json.loads(resp['construct_list'])
                    logger.debug("FabricProfile record updated successfully for id :"+str(id))
                    return Response(resp)
                except:
                    re['error']='Unable to save update on Fabric Profile'
                    logger.error(er['error'])
                    return Response(er,status=status.HTTP_400_BAD_REQUEST) 
            except:
                logger.error('Json is valid but Unable to update fabric profile with Id :'+str(id))
            return Response(resp)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        """
        To delete a Fabric Profile
        """
        er={}
        er['error']=''
        FabricProfile = self.get_object(id)
        if FabricProfile.used:
            logger.error("This FabricProfile is being used by some fabric")
            return Response("FabricProfiles is in use", status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                construct_list = json.loads(FabricProfile.construct_list)
                for item in construct_list:
                    profile_template_id=item['template_id']
                    profile_template_object=ProfileTemplate.objects.get(id=profile_template_id)
                    try:
                        profile_template_object.used_count -=1
                        profile_template_object.save()
                    except:
                        er['error']='Failed to update profile template count'
                        logger.error(er['error'])
                        return Response(er,status=status.HTTP_400_BAD_REQUEST)
                FabricProfile.delete()
                logger.debug("FabricProfile record deleted successfully for id :"+str(id))
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                er['error']='Unable to delete fabric profile'
                logger.error('Unable to delete fabric profile with id: '+str(id))
                return Response(er,status=status.HTTP_400_BAD_REQUEST)

