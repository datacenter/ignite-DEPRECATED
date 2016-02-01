from django.db import transaction

from constants import *
import linecard
from serializers import *
import switch
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_linecards(lc_type):
    lc_list = linecard.get_all_linecards(lc_type)
    serializer = LineCardSerializer(lc_list, many=True)
    return serializer.data


@transaction.atomic
def add_linecard(data, username=''):
    serializer = LineCardPutSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    lc = linecard.add_linecard(serializer.data, username)
    serializer = LineCardSerializer(lc)
    return serializer.data


def get_linecard(id):
    lc = linecard.get_linecard(id)
    serializer = LineCardSerializer(lc)
    return serializer.data


@transaction.atomic
def update_linecard(id, data, username=''):
    serializer = LineCardPutSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    lc = linecard.update_linecard(id, serializer.data, username)
    serializer = LineCardSerializer(lc)
    return serializer.data


@transaction.atomic
def delete_linecard(id):
    linecard.delete_linecard(id)


def get_all_switches(switch_type, tier):
    switches = switch.get_all_switches(switch_type, tier)
    serializer = SwitchSerializer(switches, many=True)
    return serializer.data


@transaction.atomic
def add_switch(data, username=''):
    if data[SWITCH_TYPE] == FIXED:
        serializer = SwitchFixedSerializer(data=data)
    elif data[SWITCH_TYPE] == CHASSIS:
        serializer = SwitchChassisSerializer(data=data)
    else:
        raise IgniteException(ERR_INV_SW_TYPE)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    serializer = SwitchSerializer(switch.add_switch(serializer.data, username))
    return serializer.data


def get_switch(id):
    serializer = SwitchSerializer(switch.get_switch(id))
    return serializer.data


@transaction.atomic
def update_switch(id, data, username=''):
    if data[SWITCH_TYPE] == FIXED:
        serializer = SwitchFixedSerializer(data=data)
    elif data[SWITCH_TYPE] == CHASSIS:
        serializer = SwitchChassisSerializer(data=data)
    else:
        raise IgniteException(ERR_INV_SW_TYPE)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    serializer = SwitchSerializer(switch.update_switch(id, serializer.data, username))
    return serializer.data


@transaction.atomic
def delete_switch(id):
    switch.delete_switch(id)
