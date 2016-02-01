from django.shortcuts import render

from rest_framework.response import Response

import services
from utils.baseview import BaseView
from serializers import PoolPutSerializer, PoolSerializer

# Create your views here.


class PoolListView(BaseView):

    def get(self, request, format=None):
        """
        to get all pools
        ---
      response_serializer: "PoolSerializer"

        """
        return Response(services.get_all_pools())

    def post(self, request, format=None):
        """
        to add a pool
        ---
      request_serializer: "PoolPutSerializer"
      response_serializer: "PoolSerializer"

       """
        return Response(services.add_pool(request.data, self.username))


class PoolDetailView(BaseView):

    def get(self, request, id, format=None):
        """
        to get a pool by id
        ---
      response_serializer: "PoolSerializer"

        """
        return Response(services.get_pool(int(id)))

    def put(self, request, id, format=None):
        return Response(services.update_pool(request.data, int(id),
                                             self.username))

    def delete(self, request, id, format=None):
        """
        to delete a pool
        """
        return Response(services.delete_pool(int(id)))
