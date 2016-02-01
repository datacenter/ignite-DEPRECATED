from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response

from constants import *
import services
from utils.baseview import BaseView
from serializer import TaskBriefSerializer, TaskSerializer
from serializer import WorkflowSerializer, WorkflowBriefSerializer


class TaskList(BaseView):

    def get(self, request, format=None):
        """
        to get all tasks
        ---
  response_serializer: "TaskBriefSerializer"

        """
        return Response(services.get_all_tasks())

    def post(self, request, format=None):
        """
        to add a task
        ---
  request_serializer: "TaskSerializer"
  response_serializer: "TaskBriefSerializer"

        """
        return Response(services.add_task(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class TaskDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a task by id
        ---
  response_serializer: "TaskBriefSerializer"

        """
        return Response(services.get_task(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a task
        ---
  request_serializer: "TaskSerializer"
  response_serializer: "TaskBriefSerializer"

        """
        return Response(services.update_task(int(id),
                        request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a task
        """
        services.delete_task(int(id))
        return Response()


class WorkflowList(BaseView):

    def get(self, request, format=None):
        """
        to get all workflows
        ---
  response_serializer: "WorkflowBriefSerializer"

        """
        submit = request.GET.get("submit", "")
        return Response(services.get_all_workflows(submit))

    def post(self, request, format=None):
        """
        to add a workflow
        ---
  request_serializer: "WorkflowSerializer"
  response_serializer: "WorkflowBriefSerializer"

        """
        return Response(services.add_workflow(request.data, self.username),
                        status=status.HTTP_201_CREATED)


class WorkflowDetail(BaseView):

    def get(self, request, id, format=None):
        """
        to get a workflow by id
        ---
  response_serializer: "WorkflowBriefSerializer"

        """
        return Response(services.get_workflow(int(id)))

    def put(self, request, id, format=None):
        """
        to edit a workflow
        ---
  request_serializer: "WorkflowSerializer"
  response_serializer: "WorkflowBriefSerializer"

        """
        return Response(services.update_workflow(int(id),
                        request.data, self.username))

    def delete(self, request, id, format=None):
        """
        to delete a workflow
        """
        services.delete_workflow(int(id))
        return Response()
