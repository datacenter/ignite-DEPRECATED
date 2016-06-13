from django.db.models import Q
from django.db.models import F
from django.utils import timezone
import os

import celery_tasks
from celery import result
from constants import *
import datetime
from image.models import ImageProfile
from image import image_profile
from ignite.settings import MEDIA_ROOT
import group
from models import *
import pytz
import string
from utils.exception import IgniteException
from utils.utils import parse_file
from utils.encrypt import decrypt_data
import logging
logger = logging.getLogger(__name__)


def get_all_job():
    return Job.objects.all()


def ref_count_delete(job):
    for grp in job.tasks:
        value = -1
        Group.objects.filter(pk=grp[GROUP_ID]).update(ref_count=F('ref_count')+value)


def ref_count_add(grp):
    value = 1
    Group.objects.filter(pk=grp.id).update(ref_count=F('ref_count')+value)


def get_image_details(img):
    image = {}
    image['profile_name'] = img.profile_name
    image['system_image'] = img.system_image
    image['id'] = img.id
    image['image_server_ip'] = img.image_server_ip
    image['image_server_username'] = img.image_server_username
    image['image_server_password'] = img.image_server_password
    image['is_encrypted'] = img.is_encrypted
    image['access_protocol'] = img.access_protocol

    return image


def fill_param_values(params):
    parameters = {}
    if len(params):

        for param in params:
            if param[PARAM_TYPE] == FIXED:
                parameters[param[PARAM_NAME]] = param[PARAM_VAL]

            if param[PARAM_TYPE] == IMAGE_PROFILE:
                img = image_profile.get_profile(param[PARAM_VAL])
                parameters[param[PARAM_NAME]] = get_image_details(img)

            if param[PARAM_TYPE] == EVAL:
                try:
                    parameters[param[PARAM_NAME]] = eval(param[PARAM_VALUE])
                except SyntaxError:
                    raise IgniteException("%s = %s" % (ERR_EVAL_SYNTAX,
                                                    param[PARAM_VALUE]))
    return parameters


def tasks_validation(data, options, job):
    from celery_tasks import get_all_switches
    tsk = []
    if len(data) == 0:
        raise IgniteException("Job cannot have empty task sequence")
    if options == "update":
        ref_count_delete(job)
    for task in data:
        try:
            grp = group.get_group(task[GROUP_ID])
            img = image_profile.get_profile(task[IMAGE_ID])
            if options != 'get' and img.system_image == None:
                raise IgniteException("No system image is found in the image profile: " + img.profile_name)
            if options != 'get' and task['type'] == 'epld_upgrade' and img.epld_image == None:
                raise IgniteException("No epld image is found in the image profile: " + img.profile_name)
            if task['type'] in ['epld_upgrade', 'switch_upgrade']:
                if options != 'get' and img.access_protocol != 'scp':
                    raise IgniteException("Only scp protocol is supported for image profile: " + img.profile_name)
            task["switch_count"] = len(grp.switch_list)
            # False is to say not to decrypt passwords
            switches = get_all_switches(task, False)
            task['group']['switches'] = switches
            task[IMAGE_NAME] = img.profile_name

            if task['type'] != 'custom':
                task['task_params'] = {}
                image = get_image_details(img)
                if task['type'] == 'epld_upgrade':
                    image['epld_image'] = img.epld_image
                task['task_params']['image'] = image

            if task['type'] == 'custom':
                if task['file_name'] is None and task['function'] is None:
                    raise IgniteException("Please Provide file/function name Custom task")
                try:
                    task['parameters'] = fill_param_values(task['params'])
                except:
                    raise IgniteException(ERR_IN_PARAMS)

            tsk.append(task)
            if options != "get":
                ref_count_add(grp)
        except Group.DoesNotExist as e:
            raise IgniteException("Group id "+str(task[GROUP_ID])+" not found")
        except ImageProfile.DoesNotExist as e:
            raise IgniteException("Image id "+str(task[IMAGE_ID])+" not found")
    return tsk


def add_job(data, user):
    tsk = tasks_validation(data["tasks"], "add", 0)
    jb = Job()
    jb.name = data["name"]
    date_time = datetime.datetime.strptime(data["schedule"], "%Y-%m-%dT%H:%M:%S")
    cur_time = datetime.datetime.utcnow()
    if cur_time >= date_time:
        raise IgniteException("schedule time has elapsed")
#   set timezone information
    date_time = timezone.make_aware(date_time, pytz.timezone('UTC'))
    jb.schedule = date_time
    jb.tasks = data["tasks"]
    jb.updated_by = user
    jb.save()
#   create celery task
    jb.task_id = celery_tasks.run_single_job.apply_async([jb.id, jb.schedule], eta=jb.schedule)
    jb.save()
    jb.tasks = tsk
    return jb


def get_job(id):
    jb = Job.objects.get(pk=id)
    if jb.status in ['SCHEDULED', 'RUNNING']:
        tsk = tasks_validation(jb.tasks, "get", 0)
        jb.tasks = tsk
    return jb


def assert_django_job(status, option):
    if not status == 'SCHEDULED':
        if status == 'RUNNING':
            raise IgniteException("Job is running")
        elif option == "update":
            raise IgniteException("Job is completed")


def update_job(id, data, user):
    jb = Job.objects.get(pk=id)
    assert_django_job(jb.status, "update")
    tsk = tasks_validation(data["tasks"], "update", jb)
    jb.name = data["name"]
    date_time = datetime.datetime.strptime(data["schedule"], "%Y-%m-%dT%H:%M:%S")
    cur_time = datetime.datetime.utcnow()
    if cur_time >= date_time:
        raise IgniteException("Schedule time has elapsed")
#   set timezone information
    date_time = timezone.make_aware(date_time, pytz.timezone('UTC'))
    res = result.AsyncResult(jb.task_id)
    res.revoke()
    jb.schedule = date_time
    jb.tasks = data["tasks"]
    jb.updated_by = user
    jb.task_id = celery_tasks.run_single_job.apply_async([jb.id, jb.schedule], eta=jb.schedule).task_id
    jb.save()
    jb.tasks = tsk
    return jb


def delete_job(id):
    jb = Job.objects.get(pk=id)
    assert_django_job(jb.status, "delete")
    if jb.status == "SCHEDULED":
        res = result.AsyncResult(jb.task_id)
        res.revoke()
        ref_count_delete(jb)
    jb.delete()


def get_scripts():
    fNames = os.listdir(os.path.join(MEDIA_ROOT, 'custom'))
    pynames = []
    for name in fNames:
        if name.endswith('.py'):
            pynames.append(name)
    return pynames


def get_clone_task(tasks):
    new_task = []

    for task in tasks:
        tsk = {}
        tsk[GROUP_ID] = task[GROUP_ID]
        tsk[IMAGE_ID] = task[IMAGE_ID]
        tsk[IMAGE_NAME] = task[IMAGE_NAME]
        tsk[RETRY_COUNT] = task[RETRY_COUNT]
        tsk[RUN_SIZE] = task[RUN_SIZE]
        tsk[TYPE] = task[TYPE]
        tsk[FAILURE_ACTION_GRP] = task[FAILURE_ACTION_GRP]
        tsk[FAILURE_ACTION_IND] = task[FAILURE_ACTION_IND]
        if task[TYPE] == "custom":
            tsk[FILE_NAME] = task[FILE_NAME]
            tsk[FUNCTION] = task[FUNCTION]
            tsk[PARAMS] = task[PARAMS]
        grp = {}
        grp[GROUP_NAME] = task[GROUP][GROUP_NAME]
        grp[USERNAME] = task[GROUP][USERNAME]
        grp[PASSWORD] = task[GROUP][PASSWORD]
        tsk[GROUP] = grp
        new_task.append(tsk)
    return new_task

def clone_job(data, id, username=''):
    job = Job.objects.get(id=id)
    tasks = get_clone_task(job.tasks)

    new_job = Job()
    new_job.name = data["name"]
    date_time = datetime.datetime.strptime(data["schedule"], "%Y-%m-%dT%H:%M:%S")
    cur_time = datetime.datetime.utcnow()
    if cur_time >= date_time:
        raise IgniteException("schedule time has elapsed")
    # set timezone information
    date_time = timezone.make_aware(date_time, pytz.timezone('UTC'))
    new_job.schedule = date_time
    new_job.updated_by = username
    tsk = tasks_validation(tasks, "add", 0)
    new_job.tasks = tasks
    new_job.save()
    new_job.task_id = celery_tasks.run_single_job.apply_async([new_job.id, new_job.schedule], eta=new_job.schedule)
    new_job.save()
    new_job.tasks = tsk
    return new_job
