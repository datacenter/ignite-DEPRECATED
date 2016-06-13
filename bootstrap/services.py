from django.db import transaction

import bootstrap
from serializers import *
from discovery.discoveryrule import find_dup_serial_discovery
from constants import *
from utils.exception import IgniteException
import rma

import logging
logger = logging.getLogger(__name__)



@transaction.atomic
def process_ignite_request(data):
    serializer = IgniteRequestPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    return bootstrap.ignite_request(serializer.data)


def set_switch_boot_status(data):
    serializer = SwitchBootStatusPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    return bootstrap.update_boot_status(serializer.data)


def get_all_booted_switches():
    switches = bootstrap.get_all_booted_switches()
    serializer = BootstrapSwitchSerializer(switches, many=True)
    return serializer.data


def get_rma_detail(old_serial_num):
    switch = rma.get_rma_detail(old_serial_num)
    if switch:
        serializer = RmaSerializer(switch)
        return serializer.data

    rule = rma.get_rma_rule(old_serial_num)
    if rule:
        serializer = RmaSerializer(rule)
        return serializer.data

    logger.debug(ERR_SERIAL_NOT_FOUND)
    raise IgniteException(ERR_SERIAL_NOT_FOUND)


def update_rma_detail(data):
    serializer = UpdateRmaSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    return rma.update_rma_detail(serializer.data)
