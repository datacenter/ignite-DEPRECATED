from django.db.models import ProtectedError
import os

import task
from config.constants import TRUE, FALSE
from constants import *
from fabric.constants import SERIAL_NUM
from bootstrap.constants import PKG_DIR, SCRIPT_DIR, ACCESS_METHOD, DOWNLOAD_URL
from ignite.conf import IGNITE_IP, IGNITE_USER, IGNITE_PASSWORD, ACCESS_PROTOCOL
from ignite.settings import SCRIPT_PATH
from models import Task, Workflow
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_workflows(submit):
    if submit == TRUE:
        return Workflow.objects.filter(submit=True).order_by(NAME)
    elif submit == FALSE:
        return Workflow.objects.filter(submit=False).order_by(NAME)
    else:
        return Workflow.objects.all().order_by(NAME)


def add_workflow(data, user):
    return _add_workflow(data, user)


def _add_workflow(data, user, id=0):
    logger.debug("workflow name = %s", data[NAME])

    if id:
        # get existing workflow
        workflow = Workflow.objects.get(pk=id)

        if not workflow.editable:
            raise IgniteException(ERR_WF_NOT_EDITABLE)

        for task_const in workflow.task_list:
            task.update_ref_count(task_const[TASK_ID], -1)
    else:
        # create new workflow
        workflow = Workflow()

    workflow.name = data[NAME]
    workflow.submit = data[SUBMIT]
    workflow.task_list = data[TASK_LIST]
    workflow.updated_by = user
    workflow.save()

    # increment ref count of tasks used in this workflow
    for task_const in workflow.task_list:
        task.update_ref_count(task_const[TASK_ID], 1)

    return workflow


def get_workflow(id):
    return Workflow.objects.get(pk=id)


def update_workflow(id, data, user):
    return _add_workflow(data, user, id)


def delete_workflow(id):
    workflow = Workflow.objects.get(pk=id)

    if not workflow.editable:
        raise IgniteException(ERR_WF_NOT_EDITABLE)

    # decrement ref count of tasks used in this workflow
    for task_const in workflow.task_list:
        task.update_ref_count(task_const[TASK_ID], -1)

    try:
        workflow.delete()
    except ProtectedError:
        raise IgniteException(ERR_TASK_IN_USE)


def build_workflow(wf, img, cfg_file, serial_number):
    location_list = dict()
    task_list = list()
    workflow = dict()

    for task_const in wf.task_list:
        task_obj = task.get_task(task_const[TASK_ID])
        task_data = _build_task(task_obj)

        if task_obj.id == BOOTSTRAP_CONFIG_ID:
            loc = _get_server_location()

            update_handler(task_data, BOOTSTRAP_CONF_SCRIPT)

            task_data[PARAMETERS] = _update_config_params(cfg_file,
                                                          serial_number)
        elif task_obj.id == BOOTSTRAP_IMAGE_ID:
            loc = _get_server_location()

            update_handler(task_data, BOOTSTRAP_IMAGE_SCRIPT)

            task_data[PARAMETERS] = _update_image_params(img,
                                                         serial_number)
        else:
            loc = _get_server_location(task_obj)
            task_data[PARAMETERS] = task_const[PARAMETERS]

        location_list.update({task_data[LOCATION]: loc})
        task_list.append(task_data)

    workflow.update({TASK: task_list})
    workflow.update({LOCATION: location_list})
    return workflow


def _build_task(task_obj):
    task_data = dict()
    task_data[NAME] = task_obj.name
    task_data[HANDLER] = task_obj.handler
    task_data[FUNCTION] = task_obj.function
    task_data[DESCRIPTION] = task_obj.desc
    task_data[LOCATION] = "loc_%s" % task_obj.name
    return task_data


def _update_config_params(cfg_file, serial_number):
    param = dict()
    param[SERIAL_NUM] = serial_number
    param[HOSTNAME] = IGNITE_IP
    param[PROTOCOL] = ACCESS_PROTOCOL
    param[FILE_SRC] = cfg_file
    param[USERNAME] = IGNITE_USER
    param[PASSWORD] = IGNITE_PASSWORD
    return param


def _get_server_location(task_obj=None):
    location = {}

    if not task_obj:
        location[PROTOCOL] = ACCESS_PROTOCOL
        location[HOSTNAME] = IGNITE_IP
        location[USERNAME] = IGNITE_USER
        location[PASSWORD] = IGNITE_PASSWORD
        return location

    location[PROTOCOL] = task_obj.location_access_protocol
    location[HOSTNAME] = task_obj.location_server_ip
    location[USERNAME] = task_obj.location_server_user
    location[PASSWORD] = task_obj.location_server_password
    return location


def update_handler(task_data, bootstrap_script):

    if ACCESS_PROTOCOL in [PROTO_SCP, PROTO_SFTP]:
        task_data[HANDLER] = os.path.join(SCRIPT_PATH, bootstrap_script)
    elif ACCESS_PROTOCOL == PROTO_HTTP:
        task_data[HANDLER] = os.path.join(DOWNLOAD_URL, SCRIPT_DIR, bootstrap_script)
    else:
        task_data[HANDLER] = os.path.join(SCRIPT_DIR,
                                            bootstrap_script)


def _update_image_params(img, serial_number):
    param = dict()
    param[SERIAL_NUM] = serial_number
    param[PROTOCOL] = img.access_protocol
    param[HOSTNAME] = img.image_server_ip
    param[FILE_SRC] = img.system_image
    param[USERNAME] = img.image_server_username
    param[PASSWORD] = img.image_server_password
    return param
