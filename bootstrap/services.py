from django.db import transaction

import bootstrap
from serializers import *
from utils.exception import IgniteException


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
