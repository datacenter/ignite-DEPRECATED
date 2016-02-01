from django.shortcuts import render
from django.views.generic.base import View
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, Http404
from django.http import HttpResponse
from django.http import JsonResponse

import services
import logging
from utils.baseview import BaseView
from serializers import FeatureGetBriefSerializer, FeatureSerializer
from serializers import FeatureGetSerializer
from serializers import ProfileGetAllSerializer, ProfileSerializer
from serializers import ProfileGetSerializer


logger = logging.getLogger(__name__)


class FeatureList(BaseView):
    def get(self, request, format=None):
        """
        to get all features
        ---
  response_serializer: "FeatureGetBriefSerializer"

        """
        return Response(services.get_all_features())

    def post(self, request, format=None):
        """
        to add a feature
        ---
  request_serializer: "FeatureSerializer"
  response_serializer: "FeatureGetBriefSerializer"

        """
        return Response(services.add_feature(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class FeatureDetail(BaseView):
    def get(self, request, id, format=None):
        """
        to get a feature by id
        ---
  response_serializer: "FeatureGetSerializer"

        """
        return Response(services.get_feature(id))

    def put(self, request, id, format=None):
        """
        to edit a feature
        ---
  response_serializer: "FeatureGetBriefSerializer"

        """
        return Response(services.update_feature(id, request.FILES, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a feature
        """
        return Response(services.delete_feature(id))


class ProfileList(BaseView):
    def get(self, request, format=None):
        """
        to get all profiles
        ---
  response_serializer: "ProfileGetAllSerializer"

        """
        submit = request.GET.get("submit", "")
        return Response(services.get_all_profiles(submit))

    def post(self, request, format=None):
        """
        to add a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileGetSerializer"

        """
        return Response(services.add_profile(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class ProfileDetail(BaseView):
    def get(self, request, id,  format=None):
        """
        to get a profile by id
        ---
   response_serializer: "ProfileGetSerializer"

        """
        return Response(services.get_profile(id))

    def put(self, request, id, format=None):
        """
        to edit a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileGetSerializer"

        """
        return Response(services.update_profile(id, request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a profile
        """
        return Response(services.delete_profile(id))
