import os

from django.shortcuts import render
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

import bootstrap
import services
from fabric.models import Switch
from ignite.settings import REPO_PATH
from utils.baseview import BaseView
from utils.exception import IgniteException
from serializers import IgniteRequestPostSerializer
from serializers import SwitchBootStatusPostSerializer
from serializers import BootstrapSwitchSerializer


ERR_CFG_NOT_FOUND = "Config file not found!!"
ERR_SWITCH_NOT_BOOTED = "Switch has not yet booted"


class BootstrapView(APIView):

    def post(self, request, format=None):
        """
        to process ignite request
        ---
  request_serializer: "IgniteRequestPostSerializer"

        """
        return Response(services.process_ignite_request(request.data))


class BootstrapSwitchStatusView(APIView):

    def post(self, request, format=None):
        """
        to set switch boot status
        ---
  request_serializer: "SwitchBootStatusPostSerializer"

        """
        return Response(services.set_switch_boot_status(request.data))


class BootstrapBootedSwitchView(BaseView):
    def get(self, request, format=None):
        """
        to get all booted switches
        ---
  response_serializer: "BootstrapSwitchSerializer"

        """
        return Response(services.get_all_booted_switches())


class BootstrapConfigView(BaseView):

    def get(self, request, id, format=None):
        # TODO: how to move this to services layer
        """
        to get config for switches
        """
        switch = Switch.objects.get(pk=id)

        if not switch.boot_detail:
            raise IgniteException(ERR_SWITCH_NOT_BOOTED)

        path = os.path.join(REPO_PATH, str(switch.id) + ".cfg")

        try:
            wrapper = FileWrapper(file(path))
        except:
            raise IgniteException(ERR_CFG_NOT_FOUND)

        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(path)
        return response


class BootstrapLogView(BaseView):

    def get(self, request, id, format=None):
        """
        to get logs for switches
        """
        return Response(bootstrap.get_logs(id))
