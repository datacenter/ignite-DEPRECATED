from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response

from constants import *
import services
from utils.baseview import BaseView
from serializer import ConfigletPostSerializer
from serializer import ConfigletBriefSerializer, ConfigletSerializer
from serializer import ProfileBriefSerializer, ProfileSerializer, AllProfilesSerializer


class ConfigletIndex(BaseView):

    def get(self, request, format=None):
        """
        to get all configlets
        ---
  response_serializer: "ConfigletBriefSerializer"

        """
        type = request.GET.get(CONSTRUCT_TYPE)
        return Response(services.get_all_configlet_index(type))

    def post(self, request, format=None):
        """
        to add a configlet
        ---
  request_serializer: "ConfigletPostSerializer"
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.add_configlet_index(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class ConfigletIndexDetail(BaseView):

    def get(self, request, cfgindex_id, new_version, format=None):
        """
        to get a configlet by id
        ---
  response_serializer: "ConfigletSerializer"

        """
        return Response(services.get_configlet_index(int(cfgindex_id)))

    def put(self, request, cfgindex_id, new_version, format=None):
        """
        to edit a configlet
        ---
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.update_configlet_index(int(cfgindex_id),
                        request.FILES, new_version, self.username))

    def delete(self, request, cfgindex_id, new_version, format=None):
        """
        to delete a configlet
        """
        services.delete_configlet_index(int(cfgindex_id))
        return Response()


class ConfigletDetail(BaseView):

    def get(self, request, cfgindex_id, cfg_id, new_version, format=None):
        """
        to get a configlet by id
        ---
  response_serializer: "ConfigletSerializer"

        """
        return Response(services.get_configlet(int(cfgindex_id), int(cfg_id)))

    def put(self, request, cfgindex_id, cfg_id, new_version, format=None):
        """
        to edit a configlet
        ---
  response_serializer: "ConfigletBriefSerializer"

        """
        return Response(services.update_configlet(int(cfgindex_id),
                        request.FILES, int(cfg_id), new_version, self.username))

    def delete(self, request, cfgindex_id, cfg_id, new_version, format=None):
        """
        to delete a configlet
        """
        services.delete_configlet(int(cfgindex_id), int(cfg_id))
        return Response()


class ProfileIndex(BaseView):

    def get(self, request, format=None):
        """
        to get all profiles
        ---
  response_serializer: "ProfileBriefSerializer"

        """
        submit = request.GET.get("submit", "")
        return Response(services.get_all_profile_index(submit))

    def post(self, request, format=None):
        """
        to add a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileSerializer"

        """
        return Response(services.add_profile_index(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class ProfileIndexDetail(BaseView):

    def get(self, request, prindex_id, format=None):
        """
        to get a profile by id
        ---
  response_serializer: "ProfileSerializer"

        """
        return Response(services.get_profile_index(int(prindex_id)))

    '''
    def put(self, request, prindex_id, format=None):

        """
        to edit a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileSerializer"

        """
        return Response(services.update_profile_index(int(prindex_id),
                        request.data, self.username))
    '''

    def delete(self, request, prindex_id, format=None):
        """
        to delete a profile
        """
        services.delete_profile_index(int(prindex_id))
        return Response()


class ProfileDetail(BaseView):

    def get(self, request, prindex_id, pr_id, format=None):
        """
        to get a profile by id
        ---
  response_serializer: "ProfileSerializer"

        """
        return Response(services.get_profile_by_index(int(prindex_id), int(pr_id)))

    def put(self, request, prindex_id, pr_id, format=None):
        """
        to edit a profile
        ---
  request_serializer: "ProfileSerializer"
  response_serializer: "ProfileSerializer"

        """
        return Response(services.update_profile(int(prindex_id), int(pr_id),
                        request.data, self.username))

    def delete(self, request, prindex_id, pr_id, format=None):
        """
        to delete a profile
        """
        services.delete_profile(int(prindex_id), int(pr_id))
        return Response()


class AllProfiles(BaseView):

    def get(self, request, format=None):
        """
        to get all profiles
        ---
  response_serializer: "AllProfilesSerializer"

        """
        return Response(services.get_all_profiles())
