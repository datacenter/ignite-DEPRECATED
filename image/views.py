from django.shortcuts import render

from rest_framework.response import Response

import image_profile
from constants import *
from serializers import ImageProfileSerializer, ImageProfilePutSerializer, ImageProfileListSerializer
from utils.exception import IgniteException
from utils.baseview import BaseView


class ImageProfileListView(BaseView):

    def get(self, request, format=None):
        """
        to get all image profiles
        ---
        request_serializer: "ImageProfileSerializer"

        """
        state = request.GET.get(STATE)
        profiles = image_profile.get_all_profiles(state)
        serializer = ImageProfileListSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        to add a image profile
        ---
  request_serializer: "ImageProfileSerializer"
  response_serializer: "ImageProfilePutSerializer"

        """
        serializer = ImageProfileSerializer(data=request.data)

        if not serializer.is_valid():
            raise IgniteException(serializer.errors)

        profile = image_profile.add_profile(serializer.data, user=self.username)
        serializer = ImageProfileListSerializer(profile)
        return Response(serializer.data)


class ImageProfileDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get an image profile by id
        ---
  response_serializer: "ImageProfilePutSerializer"

        """
        profile = image_profile.get_profile(int(id))
        serializer = ImageProfilePutSerializer(profile)
        return Response(serializer.data)

    def put(self, request, id, format=None):
        """
        to edit an image profile
        ---
  request_serializer: "ImageProfileSerializer"
  response_serializer: "ImageProfilePutSerializer"

        """
        serializer = ImageProfileSerializer(data=request.data)

        if not serializer.is_valid():
            raise IgniteException(serializer.errors)

        profile = image_profile.add_profile(serializer.data, user=self.username, id=int(id))
        serializer = ImageProfileListSerializer(profile)
        return Response(serializer.data)

    def delete(self, request, id, format=None):
        """
        to delete an image profile

        """
        image_profile.delete_profile(int(id))
        return Response()
