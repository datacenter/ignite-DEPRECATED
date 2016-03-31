import os

from django.shortcuts import render
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from constants import *
import bootstrap
import services
from fabric.models import Switch
from ignite.settings import REPO_PATH, PKG_PATH, SCRIPT_PATH
from utils.baseview import BaseView
from utils.exception import IgniteException
from serializers import IgniteRequestPostSerializer
from serializers import SwitchBootStatusPostSerializer
from serializers import BootstrapSwitchSerializer
from serializers import RmaSerializer
from serializers import UpdateRmaSerializer


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


class RmaSerialSearchView(BaseView):

    def get(self, request, id, format=None):
        """
        to get rma details
        ---
  response_serializer: "RmaSerializer"

        """
        return Response(services.get_rma_detail(id))


class RmaSerialUpdateView(BaseView):

    def post(self, request, format=None):
        """
        to update rma details
        ---
  request_serializer: "UpdateRmaSerializer"

        """
        return Response(services.update_rma_detail(request.data))


class BootstrapDownloadConfigView(APIView):

    def get(self, request, id, format=None):
        # TODO: how to move this to services layer
        """
        to download config
        """
        switch = Switch.objects.get(pk=id)

        path = os.path.join(REPO_PATH, str(switch.id) + ".cfg")

        try:
            wrapper = FileWrapper(file(path))
        except IOError:
            raise IgniteException(ERR_CFG_NOT_FOUND)

        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(path)
        return response


class YamlView(APIView):

    def get(self, request, id, format=None):
        """
        to download YAML
        """
        switch = Switch.objects.get(pk=id)

        path = os.path.join(REPO_PATH, str(switch.id) + ".yml")

        try:
            wrapper = FileWrapper(file(path))
        except IOError:
            raise IgniteException(ERR_YML_NOT_FOUND)

        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(path)
        return response


class BootstrapScriptView(APIView):

    def get(self, request, script_name, format=None):
        """
        to download boot scripts
        """
        path = os.path.join(SCRIPT_PATH, str(script_name))

        try:
            wrapper = FileWrapper(file(path))
        except IOError:
            raise IgniteException(ERR_SCRIPT_NOT_FOUND)

        response = HttpResponse(wrapper, content_type='text/plain')
        response['Content-Length'] = os.path.getsize(path)
        return response


class BootstrapPackageView(APIView):

    def get(self, request, pkg_name, format=None):
        """
        to download PyYAML packages
        """
        path = os.path.join(PKG_PATH, str(pkg_name))
        response = HttpResponse(FileWrapper(file(path)), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=str(pkg_name)'
        return response
