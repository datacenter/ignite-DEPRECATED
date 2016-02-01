from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response

from constants import *
import services
from utils.baseview import BaseView
from serializer import ConfigletPostSerializer
from serializer import ConfigletBriefSerializer, ConfigletSerializer
from serializer import ProfileBriefSerializer, ProfileSerializer


class ConfigletList(BaseView):

    def get(self, request, format=None):
        """
        to get all configlets
        ---
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.get_all_configlets())

    def post(self, request, format=None):
        """
        to add a configlet
        ---
  request_serializer: "ConfigletPostSerializer"
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.add_configlet(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class ConfigletDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a configlet by id
        ---
  response_serializer: "ConfigletSerializer"

        """
        return Response(services.get_configlet(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a configlet
        ---
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.update_configlet(int(id),
                        request.FILES, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a configlet
        """
        services.delete_configlet(int(id))
        return Response()


class ProfileList(BaseView):

    def get(self, request, format=None):
        """
        to get all profiles
        ---
  response_serializer: "ProfileBriefSerializer"

        """
        submit = request.GET.get("submit", "")
        return Response(services.get_all_profiles(submit))

    def post(self, request, format=None):
        """
        to add a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileSerializer"

        """
        return Response(services.add_profile(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class ProfileDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a profile by id
        ---
  response_serializer: "ProfileSerializer"

        """
        return Response(services.get_profile(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileSerializer"

        """
        return Response(services.update_profile(int(id),
                        request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a profile
        """
        services.delete_profile(int(id))
        return Response()
