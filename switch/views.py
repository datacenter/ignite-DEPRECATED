from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response

from constants import ALL
import services
from utils.exception import IgniteException
from utils.baseview import BaseView
from serializers import LineCardPutSerializer, LineCardSerializer
from serializers import SwitchSerializer, SwitchChassisSerializer


class LineCardListView(BaseView):

    def get(self, request, format=None):
        """
        to get all linecards
        ---
   response_serializer: "LineCardSerializer"

        """
        lc_type = request.GET.get("type", ALL)
        return Response(services.get_all_linecards(lc_type))

    def post(self, request, format=None):
        """
        to add a linecard
        ---
   request_serializer: "LineCardPutSerializer"
   response_serializer: "LineCardSerializer"

        """
        return Response(services.add_linecard(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class LineCardDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get a linecard by id
        ---
   response_serializer: "LineCardSerializer"

        """
        return Response(services.get_linecard(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a linecard
        ---
   request_serializer: "LineCardPutSerializer"
   response_serializer: "LineCardSerializer"

        """
        return Response(services.update_linecard(int(id), request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a linecard
        """
        services.delete_linecard(int(id))
        return Response()


class SwitchListView(BaseView):

    def get(self, request, format=None):
        """
        to get all switch
        ---
  response_serializer: "SwitchSerializer"

        """
        switch_type = request.GET.get("type", ALL)
        tier = request.GET.get("tier", ALL)
        return Response(services.get_all_switches(switch_type, tier))

    def post(self, request, format=None):
        """
        to add a switch
        ---
  request_serializer: "SwitchChassisSerializer"
  response_serializer: "SwitchSerializer"

        """
        return Response(services.add_switch(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class SwitchDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get a switch by id
        ---
  response_serializer: "SwitchSerializer"

        """
        return Response(services.get_switch(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a switch
        ---
  request_serializer: "SwitchChassisSerializer"
  response_serializer: "SwitchSerializer"

        """
        return Response(services.update_switch(int(id), request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a switch
        """
        services.delete_switch(int(id))
        return Response()

class SwitchModelBootProgressView(BaseView):

    def get(self, request, id, format=None):
        return Response(services.get_progress_switches(int(id)))


class SwitchModelBootFailView(BaseView):

    def get(self, request, id, format=None):
        return Response(services.get_fail_switches(int(id)))


class SwitchModelBootSuccessView(BaseView):

    def get(self, request, id, format=None):
        return Response(services.get_success_switches(int(id)))
