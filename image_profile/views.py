from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404, JsonResponse
from usermanagement.utils import RequestValidator
from django.contrib.auth.models import User
import logging
from django.core.servers.basehttp import FileWrapper
from collections import Counter

#user defined imports
from models import ImageProfile
from image_profile.ImageProfileSerializer import ImageProfileGetSerializer, ImageProfilePostSerializer,ImageProfilePutSerializer

logger = logging.getLogger(__name__)

class ImageProfileList(APIView):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ImageProfileList, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        """
        To get list of image profiles
        ---
  response_serializer: "ImageProfileGetSerializer"

        """
        image_list = ImageProfile.objects.order_by('image_profile_name')
        serializer = ImageProfileGetSerializer(image_list, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        To add an Image Profile
        ---
  request_serializer: "ImageProfilePostSerializer"
  response_serializer: "ImageProfileGetSerializer"

        """
        serializer = ImageProfilePostSerializer(data=request.data)
        me = RequestValidator(request.META)
        if serializer.is_valid():
            image_obj = ImageProfile()
#             image_obj.user_id = me.user_is_exist().user_id
            image_obj.image_profile_name = request.data['image_profile_name']
            image_obj.image = request.data['image']
            image_obj.imageserver_ip = request.data['imageserver_ip']
            image_obj.username = request.data['username']
            image_obj.password = request.data['password']
            image_obj.access_protocol = request.data['access_protocol']
            try:
                image_obj.save()
            except:
                Err_msg = 'Failed to save image profile object'
                logger.error(Err_msg)
                return Response(Err_msg, status=status.HTTP_400_BAD_REQUEST)
            serializer = ImageProfileGetSerializer(image_obj)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ImageProfileListDetail(APIView):

    def dispatch(self,request, *args, **kwargs):
        me = RequestValidator(request.META)
        if me.user_is_exist():
            return super(ImageProfileListDetail, self).dispatch(request,*args, **kwargs)
        else:
            resp = me.invalid_token()
            return JsonResponse(resp,status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id, format=None):
        """
        To get a particular Image profile
        ---
  response_serializer: "ImageProfileGetSerializer"

        """
        try:
            image_obj = ImageProfile.objects.get(pk=id)
            serializer = ImageProfileGetSerializer(image_obj)
            return Response(serializer.data)
        except:
            Err_msg = 'Image profile not found with id: '+str(id)
            logger.error(Err_msg)
            return Response(Err_msg, status=status.HTTP_400_BAD_REQUEST)

    def put (self, request, id, format=None):
        """
        To edit an Image profile
        ---
  request_serializer: "ImageProfilePutSerializer"
  response_serializer: "ImageProfileGetSerializer"

        """
        try:
            obj = ImageProfile.objects.get(pk=id)
            if obj.image_profile_name == request.data['image_profile_name']:
                serializer = ImageProfilePutSerializer(data=request.data)
            else:
                serializer = ImageProfilePostSerializer(data=request.data)
            if serializer.is_valid():
                obj.image_profile_name = request.data['image_profile_name']
                obj.image = request.data['image']
                obj.imageserver_ip = request.data['imageserver_ip']
                obj.username = request.data['username']
                obj.password = request.data['password']
                obj.access_protocol = request.data['access_protocol']
                obj.save()
                serializer = ImageProfileGetSerializer(obj)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            Err_msg = 'Image profile not found with id: '+str(id)
            logger.error(Err_msg)
            return Response(Err_msg, status=status.HTTP_400_BAD_REQUEST)

    def delete (self, request, id, format=None):
        """
        To delete an Image Profile
        """
        try:
           obj = ImageProfile.objects.get(pk=id) 
           obj.delete()
           logger.info('image profile deleted successfully')
           return Response(status=status.HTTP_204_NO_CONTENT)
        except:
           Err_msg = 'Image profile not found with id: '+str(id)
           logger.error(Err_msg)
           return Response(Err_msg, status=status.HTTP_400_BAD_REQUEST)
    
    
