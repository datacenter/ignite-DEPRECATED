from django.db import transaction

import group
import job
from pool.models import PoolEntry
from serializer import *
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_groups():
    grp = group.get_all_groups()
    serializer = GroupDetailSerializer(grp, many=True)
    return serializer.data


def get_all_groups_fabric(fab_id):
    grp = group.get_all_groups_fabric(fab_id)
    serializer = GroupDetailSerializer(grp, many=True)
    return serializer.data


@transaction.atomic
def add_group(data, fab_id, username=''):
    serializer = GroupPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    grp = group.add_group(serializer.data, fab_id, username)
    serializer = GroupBriefSerializer(grp)
    return serializer.data


@transaction.atomic
def update_group(data, fab_id, grp_id, username=''):
    serializer = GroupPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    grp = group.update_group(serializer.data, fab_id, grp_id, username)
    serializer = GroupBriefSerializer(grp)
    return serializer.data


@transaction.atomic
def delete_group(id):
    group.delete_group(id)


def get_group(gid):
    grp = group.get_group(gid)
    serializer = GroupDetailSerializer(grp)
    return serializer.data


def get_all_job():
    jb = job.get_all_job()
    serializer = JobBriefSerializer(jb, many=True)
    return serializer.data


@transaction.atomic
def add_job(data, username=''):
    serializer = JobPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    jb = job.add_job(serializer.data, username)
    serializer = JobDetailSerializer(jb)
    return serializer.data


def get_job(id):
    jb = job.get_job(id)
    serializer = JobDetailSerializer(jb)
    return serializer.data


@transaction.atomic
def update_job(id, data, username=''):
    serializer = JobPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    jb = job.update_job(id, serializer.data, username)
    serializer = JobDetailSerializer(jb)
    return serializer.data


@transaction.atomic
def delete_job(id):
    jb = job.delete_job(id)


def get_scripts():
    return job.get_scripts()


@transaction.atomic
def clone_job(data, id, username=''):
    serializer = JobCloneSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    jb = job.clone_job(serializer.data, id, username)
    serializer = JobDetailSerializer(jb)
    return serializer.data
