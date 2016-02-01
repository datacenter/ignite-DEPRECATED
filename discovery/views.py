from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response


from constants import *
import services
from utils.exception import IgniteException
from utils.baseview import BaseView
from serializer import DiscoveryRuleGetSerializer
from serializer import DiscoveryRuleSerialIDSerializer
from serializer import DiscoveryRuleGetDetailSerializer


class DiscoveryRuleList(BaseView):
    def get(self, request, format=None):
        """
        to get all discovery rules
        ---
  response_serializer: "DiscoveryRuleGetSerializer"

        """
        return Response(services.get_all_discoveryrules())

    def post(self, request, format=None):
        """
        to add a discovery Rule
        ---
  request_serializer: "DiscoveryRuleSerialIDSerializer"
  response_serializer: "DiscoveryRuleGetSerializer"

        """
        return Response(services.add_discoveryrule(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class DiscoveryRuleDetailList(BaseView):
    def get(self, request, id, format=None):
        """
        to get a discovery rule by id
        ---
  response_serializer: "DiscoveryRuleGetDetailSerializer"

        """
        return Response(services.get_discoveryrule(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a discovery rule
        ---
  request_serializer: "DiscoveryRuleSerialIDSerializer"
  response_serializer: "DiscoveryRuleGetSerializer"

        """
        return Response(services.update_discoveryrule(int(id), request.data,
                        self.username))

    def delete(self, request, id, format=None):
        """
        to delete a discovery Rule
        """
        services.delete_discoveryrule(int(id))
        return Response(status=status.HTTP_204_NO_CONTENT)
