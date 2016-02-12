from django.db.models import Q
from django.db.models import F
from django.utils import timezone

import celery_tasks
from celery import result
import datetime
from image.models import ImageProfile
from image import image_profile
import group
from models import *
import pytz
import string
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_all_job():
    return Job.objects.all()


def ref_count_delete(job):
    for grp in job.tasks:
        value = -1
        Group.objects.filter(pk=grp["group_id"]).update(ref_count=F('ref_count')+value)


def ref_count_add(grp):
    value = 1
    Group.objects.filter(pk=grp.id).update(ref_count=F('ref_count')+value)


def tasks_validation(data, options, job):
    tsk = []
    if len(data) == 0:
        raise IgniteException("Job cannot have empty task sequence")
    if options == "update":
        ref_count_delete(job)
    for task in data:
        try:
            grp = group.get_group(task["group_id"])
            img = image_profile.get_profile(task["image_id"])
            if task["type"] == "switch_upgrade":
		if not img.system_image:
		    raise IgniteException("No system image found in " + img.profile_name)
	    if task["type"] != "switch_upgrade":
                raise IgniteException("Only switch upgrade is supported")
            task["switch_count"] = len(grp.switch_list)
            task["group_name"] = grp.name
            task["image_name"] = img.profile_name
            tsk.append(task)
            if options != "get":
                ref_count_add(grp)
        except Group.DoesNotExist as e:
            raise IgniteException("Group id "+str(task["group_id"])+" not found")
        except ImageProfile.DoesNotExist as e:
            raise IgniteException("Image id "+str(task["image_id"])+" not found")
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
