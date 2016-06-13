from django.db.models import F
import string

from constants import *
from models import Task
from utils.exception import IgniteException
from utils.utils import parse_file
from utils.encrypt import encrypt_data, decrypt_data

import logging
logger = logging.getLogger(__name__)


def get_all_tasks():
    return Task.objects.all().order_by(NAME)


def add_task(data, user):
    return _add_task(data, user)


def _add_task(data, user, id=0):
    logger.debug("Task name = %s", data[NAME])

    if id:
        # get existing task
        task = Task.objects.get(pk=id)

        if not task.editable:
            raise IgniteException(ERR_TASK_NOT_EDITABLE)
    else:
        # create new task
        task = Task()

    task.name = data[NAME]
    task.handler = data[HANDLER]
    task.function = data[FUNCTION]
    task.desc = data[DESCRIPTION]
    task.location_access_protocol = data[LOC_ACCESS_PROTO]
    task.location_server_ip = data[LOC_SERVER_IP]
    task.location_server_user = data[LOC_SERVER_USER]
    password = encrypt_data(data[LOC_SERVER_PASSWORD])
    task.location_server_password = password
    task.is_encrypted = True
    task.parameters = data[PARAMETERS]
    task.updated_by = user
    task.save()
    return task


def get_task(id):
    return Task.objects.get(pk=id)


def update_task(id, data, user):
    return _add_task(data, user, id)


def delete_task(id):
    task = Task.objects.get(pk=id)

    if not task.editable:
        raise IgniteException(ERR_TASK_NOT_EDITABLE)

    if task.ref_count:
        raise IgniteException(ERR_TASK_IN_USE)

    task.delete()


def update_ref_count(id, value):
    Task.objects.filter(pk=id).update(ref_count=F('ref_count')+value)
