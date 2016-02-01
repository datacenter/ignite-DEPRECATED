from django.db import transaction
import ast
import json


from utils.exception import IgniteException
from constants import *
from serializer import *
import discoveryrule


import logging
logger = logging.getLogger(__name__)


def get_all_discoveryrules():
    rules = discoveryrule.get_all_discoveryrules()
    serializer = DiscoveryRuleGetSerializer(rules, many=True)
    return serializer.data


@transaction.atomic
def add_discoveryrule(data, username=''):
    serializer = ''
    if data[MATCH] != SERIAL_NUM:
        serializer = DiscoveryRuleSerializer(data=data)
    else:
        serializer = DiscoveryRuleSerialIDSerializer(data=data)

    if not serializer.is_valid():
        logger.debug("serializer errors")
        raise IgniteException(serializer.errors)

    disrule = discoveryrule.add_discoveryrule(data, username)
    serializer = DiscoveryRuleGetSerializer(disrule)
    return serializer.data


def get_discoveryrule(id):
    disrule = discoveryrule.get_discoveryrule(id)
    serializer = DiscoveryRuleGetDetailSerializer(disrule)
    return serializer.data


@transaction.atomic
def update_discoveryrule(id, data, username=''):
    serializer = ''
    if data[MATCH] != SERIAL_NUM:
        serializer = DiscoveryRuleSerializer(data=data)
    else:
        serializer = DiscoveryRuleSerialIDSerializer(data=data)
    if not serializer.is_valid():
        logger.debug("serializer errors")
        raise IgniteException(serializer.errors)

    disrule = discoveryrule.update_discoveryrule(id, data, username)
    serializer = DiscoveryRuleGetSerializer(disrule)
    return serializer.data


@transaction.atomic
def delete_discoveryrule(id):
    discoveryrule.delete_discoveryrule(id)
