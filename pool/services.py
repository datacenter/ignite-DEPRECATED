from django.db import transaction

import pool
from serializers import *
from utils.exception import IgniteException


def get_all_pools():
    pools = pool.get_all_pools()
    serializer = PoolSerializer(pools, many=True)
    return serializer.data


@transaction.atomic
def add_pool(data, username=''):
    serializer = PoolPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    pl = pool.add_pool(serializer.data, username)
    serializer = PoolSerializer(pl)
    return serializer.data


@transaction.atomic
def update_pool(data, id, username=''):
    serializer = PoolPutSerializer(data=data, many=True)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    pl = pool.update_pool(serializer.data, id, username)
    serializer = PoolSerializer(pl)
    return serializer.data


def get_pool(id):
    pl = pool.get_pool(id)
    serializer = PoolSerializer(pl)
    return serializer.data


@transaction.atomic
def delete_pool(id):
    pool.delete_pool(id)
