from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

import aaaserver
import backup
import services
from serializers import *
from utils.baseview import AdminView


class AAAServerListView(AdminView):
    def get(self, request, format=None):
        """
        To get all AAA servers
        ---
  response_serializer: "ServerSerializer"
        """
        return Response(services.get_all_servers())

    def post(self, request, format=None):
        """
        To Add a AAA server
        ---
  request_serializer: "ServerSerializer"
  response_serializer: "ServerSerializer"
        """
        return Response(services.add_server(request.data, self.username))


class AAAServerDetailView(AdminView):
    def get(self, request, id, format=None):
        """
        To get AAA server details
        ---
  response_serializer: "ServerSerializer"
        """
        return Response(services.get_server(int(id)))

    def put(self, request, id, format=None):
        """
        To edit a AAA server details
        ---
  request_serializer: "ServerSerializer"
  response_serializer: "ServerSerializer"
        """
        return Response(services.update_server(request.data, int(id),
                                               self.username))

    def delete(self, request, id, format=None):
        """
        To delete a AAA server
        """
        services.delete_server(int(id))
        return Response()


class AAAUserListView(AdminView):
    def get(self, request, format=None):
        """
        To get list of users added by AAA
        ---
  response_serializer: "UserSerializer"
        """
        return Response(services.get_all_users())

    def post(self, request, format=None):
        """
        To add an user
        ---
  request_serializer: "UserCreateSerializer"
  response_serializer: "UserSerializer"
        """
        return Response(services.add_user(request.data))


class AAAUserDetailView(AdminView):
    def get(self, request, id, format=None):
        """
        To get an User by id
        ---
  response_serializer: "UserDetailSerializer"
        """
        return Response(services.get_user(id))

    def put(self, request, id, format=None):
        """
        To edit an User
        ---
  request_serializer: "UserPutSerializer"
  response_serializer: "UserSerializer"
        """
        return Response(services.update_user(request.data, id))

    def delete(self, request, id, format=None):
        """
        To delete an user
        """
        services.delete_user(id)
        return Response()


class IgniteBackupView(AdminView):
    def get(self, request, format=None):
        """
        TO get list of backup files
        """
        return Response(backup.get_list())

    def post(self, request, format=None):
        """
        To reqeust Backup media and database
        """
        return Response(backup.create_backup())

    def delete(self, request, format=None):
        """
        To delete a backup file
        """
        backup.delete_backup(request.data)
        return Response()


class IgniteBackupDetailView(APIView):
    def get(self, request, fn, format=None):
        """
        To download Backup file
        """
        return backup.download_backup(fn)
