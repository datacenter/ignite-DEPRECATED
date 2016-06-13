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


class GroupListPerFabric(BaseView):

    def get(self, request, fab_id, format=None):
        """
        to get all Groups for given fabric id
        ---
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.get_all_groups_fabric(fab_id))

    def post(self, request, fab_id, format=None):
        """
        to add a Group
        ---
  request_serializer: "GroupPostSerializer"
  response_serializer: "GroupBriefSerializer"

        """
        return Response(services.add_group(request.data, fab_id, self.username),
                        status=status.HTTP_201_CREATED)


class GroupDetail(BaseView):

    def get(self, request, fab_id, grp_id, format=None):
        """
        to get a Group by id
        ---
  response_serializer: "GroupDetailSerializer"

        """
        return Response(services.get_group(int(grp_id)))

    def put(self, request, fab_id, grp_id, format=None):
        """
        to edit a Group
        ---
  request_serializer: "GroupPostSerializer"
  response_serializer: "GroupBriefSerializer"

        """
        return Response(services.update_group(request.data,
                                              int(fab_id), int(grp_id),
                                              self.username))

    def delete(self, request, fab_id, grp_id, format=None):
        services.delete_group(int(grp_id))
        return Response()


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


class ScriptList(BaseView):

    def get(self, request, format=None):
        """
        to get list of user defined scripts
        """
        return Response(services.get_scripts())


class JobCloneView(BaseView):
    def post(self, request, id, format=None):
        """
        to clone a job
        ---
  request_serializer: "JobCloneSerializer"
  response_serializer: "JobDetailSerializer"

        """
        return Response(services.clone_job(request.data, id, self.username))
