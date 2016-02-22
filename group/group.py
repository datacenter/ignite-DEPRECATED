from django.db.models import Q

import datetime
from bootstrap.constants import BOOT_SUCCESS
from fabric.models import Switch
from models import *
from pool.models import PoolEntry
import string
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_all_groups():
    grps = Group.objects.all()
    group = []
    for grp in grps:
        grp.switch_list = GroupSwitch.objects.filter(group_id=grp.id)
        group.append(grp)
    return group


def add_group(data, user):
    grp = Group()
    grp.name = data["name"]
    grp.username = data["username"]
    grp.password = data["password"]
    grp.updated_by = user
    grp.save()
    return grp


def get_group(gid):
    grp = Group.objects.get(pk=gid)
    grp.switch_list = GroupSwitch.objects.filter(group_id=gid)
    return grp


def update_group(id, data, user):
    grp = Group.objects.get(pk=id)
    grp.name = data["name"]
    grp.username = data["username"]
    grp.password = data["password"]
    grp.updated_by = user
    grp.save()
    return grp


def delete_group(id):
    grp = Group.objects.get(pk=id)
    if not (grp.ref_count == 0):
        raise IgniteException("Group is in use")
    grp.delete()


def add_switch(gid, data, user):
    count = 0
    error = []
    for switch in data:
        mes = {}
        if not Switch.objects.filter(id=switch["switch_id"],
                                     boot_detail__isnull=False,
                                     boot_detail__boot_status__icontains=BOOT_SUCCESS):
            mes[switch["switch_id"]] = "switch is not booted"
            count = count+1
        else:
            mes[switch["switch_id"]] = ""
        error.append(mes)
    if not (count == 0):
        raise IgniteException(error)
    for switch in data:
        if not (GroupSwitch.objects.filter(group__id=gid, grp_switch__id=switch["switch_id"]).count() == 0):
            continue
        sw = GroupSwitch()
        grp = Group.objects.get(pk=gid)
        sw.group = grp
        fsw = Switch.objects.get(id=switch["switch_id"])
        sw.grp_switch = fsw
        sw.save()


def delete_switch(gid, data):
    grp = Group.objects.get(pk=gid)
    for switch in data:
        try:
            gsw = GroupSwitch.objects.get(group__id=gid,
                                          grp_switch__id=switch["switch_id"])
            gsw.delete()
        except GroupSwitch.DoesNotExist as e:
            raise IgniteException("switch id "+str(switch["switch_id"])+" not found")
