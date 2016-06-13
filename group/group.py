from django.db.models import Q

import datetime
from bootstrap.constants import BOOT_SUCCESS
from fabric.models import Fabric, Switch
from models import *
from pool.models import PoolEntry
import string
from utils.exception import IgniteException
from utils.utils import parse_file
from utils.encrypt import encrypt_data, decrypt_data


import logging
logger = logging.getLogger(__name__)


def get_all_groups():
    grps = Group.objects.all()
    group = []
    for grp in grps:
        grp.switch_list = GroupSwitch.objects.filter(group_id=grp.id)
        group.append(grp)
    return group


def get_all_groups_fabric(fab_id):
    grps = Group.objects.filter(fabric_id=fab_id)
    group = []
    for grp in grps:
        grp.switch_list = GroupSwitch.objects.filter(group_id=grp.id)
        group.append(grp)
    return group


def maintenance_group_count(fab_id):
    return Group.objects.filter(fabric_id=fab_id).count()


def add_group(data, fab_id, user):
    grp = Group()
    grp.name = data["name"]
    grp.username = data["username"]
    password = encrypt_data(data["password"])
    grp.password = password
    grp.is_encrypted = True
    grp.updated_by = user
    grp.fabric = Fabric.objects.get(id=fab_id)
    grp.save()
    add_switches(data['switch_list'], fab_id, grp.id,  user)
    return grp


def get_group(gid):
    grp = Group.objects.get(pk=gid)
    grp.switch_list = GroupSwitch.objects.filter(group_id=gid)
    return grp


def update_group(data, fab_id, grp_id, user):
    grp = Group.objects.get(pk=grp_id)
    grp.name = data["name"]
    grp.username = data["username"]
    password = encrypt_data(data["password"])
    grp.password = password
    grp.is_encrypted = True
    grp.updated_by = user
    delete_switches(grp_id)
    add_switches(data['switch_list'], fab_id, grp_id,  user)
    grp.save()
    return grp


def delete_group(id):
    grp = Group.objects.get(pk=id)
    if not (grp.ref_count == 0):
        raise IgniteException("Group is in use")
    grp.delete()


def add_switches(data, fab_id, gid, user):
    count = 0
    error = []
    for switch in data:
        mes = {}
        if not Switch.objects.filter(id=switch["switch_id"],
                                     topology_id=fab_id,
                                     topology__is_fabric=True,
                                     boot_detail__isnull=False,
                                     boot_detail__boot_status=BOOT_SUCCESS):
            mes[switch["switch_id"]] = "switch is not booted"
            count = count+1
        else:
            mes[switch["switch_id"]] = ""
        error.append(mes)
    if count:
        raise IgniteException(error)
    for switch in data:
        if not (GroupSwitch.objects.filter(group__id=gid, grp_switch__id=switch["switch_id"]).count()==0):
            continue
        sw = GroupSwitch()
        grp = Group.objects.get(pk=gid)
        sw.group = grp
        fsw = Switch.objects.get(id=switch["switch_id"])
        sw.grp_switch = fsw
        sw.save()


def delete_switches(gid):
    grp = Group.objects.get(pk=gid)
    try:
        GroupSwitch.objects.filter(group__id=gid).delete()
    except GroupSwitch.DoesNotExist as e:
        pass
