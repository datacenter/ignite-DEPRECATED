from django.db import transaction

import task
from constants import *
from models import Task, Workflow
import workflow
from serializer import *
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_tasks():
    tasks = task.get_all_tasks()
    serializer = TaskBriefSerializer(tasks, many=True)
    return serializer.data


@transaction.atomic
def add_task(data, username=''):
    serializer = TaskSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    task_obj = task.add_task(serializer.data, username)
    serializer = TaskBriefSerializer(task_obj)
    return serializer.data


def get_task(id):
    task_obj = task.get_task(id)
    serializer = TaskSerializer(task_obj)
    return serializer.data


@transaction.atomic
def update_task(id, data, username=''):
    task_obj = task.update_task(id, data, username)
    serializer = TaskBriefSerializer(task_obj)
    return serializer.data


@transaction.atomic
def delete_task(id):
    task.delete_task(id)


def get_all_workflows(submit):
    workflows = workflow.get_all_workflows(submit)
    serializer = WorkflowBriefSerializer(workflows, many=True)
    return serializer.data


@transaction.atomic
def add_workflow(data, username=''):
    serializer = WorkflowSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    wf = workflow.add_workflow(serializer.data, username)
    serializer = WorkflowSerializer(wf)
    return serializer.data


def get_workflow(id):
    serializer = WorkflowSerializer(workflow.get_workflow(id))
    return serializer.data


@transaction.atomic
def update_workflow(id, data, username=''):
    serializer = WorkflowSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    wf = workflow.update_workflow(id, serializer.data, username)
    serializer = WorkflowSerializer(wf)
    return serializer.data


@transaction.atomic
def delete_workflow(id):
    workflow.delete_workflow(id)
