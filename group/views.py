from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response

from serializer import *
import services
from utils.baseview import BaseView


class GroupList(BaseView):

    def get(self, request, format=None):
        """
        to get all Groups
        ---
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.get_all_groups())

    def post(self, request, format=None):
        """
        to add a Group
        ---
  request_serializer: "GroupPostSerializer"
  response_serializer: "GroupBriefSerializer"

        """
        return Response(services.add_group(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class GroupDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a Group by id
        ---
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.get_group(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a Group
        ---
  request_serializer: "GroupPostSerializer"
  response_serializer: "GroupBriefSerializer"

        """
        return Response(services.update_group(int(id),
                        request.data, self.username))

    def delete(self, request, id, format=None):
        services.delete_group(int(id))
        return Response()


class GroupSwitchList(BaseView):

    def post(self, request, gid, format=None):
        """
        to add a switches into Group
        ---
  request_serializer: "GroupSwitchPostSerializer"
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.add_switch(int(gid), request.data,
                        self.username))

    def delete(self, request, gid, format=None):
        """
        to delete a switches from Group
        ---
  request_serializer: "GroupSwitchPostSerializer"
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.delete_switch(int(gid), request.data))


class JobList(BaseView):

    def get(self, request, format=None):
        """
        to get all Jobs
        ---
  response_serializer: "JobBriefSerializer"

        """
        return Response(services.get_all_job())

    def post(self, request, format=None):
        """
        to add a job
        ---
  request_serializer: "JobPostSerializer"
  response_serializer: "JobDetailSerializer"

        """
        return Response(services.add_job(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class JobDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a Job by id
        ---
  response_serializer: "JobDetailSerializer"

        """
        return Response(services.get_job(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a Job
        ---
  request_serializer: "JobPostSerializer"
  response_serializer: "JobDetailSerializer"

        """
        return Response(services.update_job(int(id),
                        request.data, self.username))

    def delete(self, request, id, format=None):
        services.delete_job(int(id))
        return Response()
