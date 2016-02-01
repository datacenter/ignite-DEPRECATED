from django.db.models import F
from netaddr import IPAddress, IPNetwork

from constants import *
from fabric.models import Fabric, Switch
from models import Pool, PoolEntry
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_pools():
    pools = Pool.objects.all()
    pool_list = list()
    for pool in pools:
        pool.used = len(PoolEntry.objects.filter(pool_id=pool.id).
                        exclude(switch=None))
        pool.available = len(PoolEntry.objects.filter(pool_id=pool.id).
                             filter(switch=None))
        pool_list.append(pool)

    return pool_list


def add_pool(data, user):
    _validate_pool(data[BLOCKS], data[TYPE])

    # create new pool
    pool = Pool()
    pool.name = data[NAME]
    pool.type = data[TYPE]
    pool.scope = data[SCOPE]
    pool.blocks = data[BLOCKS]
    pool.updated_by = user
    pool.save()

    if pool.scope == FABRIC:
        return pool

    # if scope is global create pool entries
    if pool.type == INTEGER:
        _create_integer_pool(pool, pool.blocks)
    elif pool.type == IPV4:
        _create_ipv4_pool(pool, pool.blocks)
    elif pool.type == IPV6:
        _create_ipv6_pool(pool, pool.blocks)

    return pool


def update_pool(data, id, user):
    pool = get_pool(id)
    blocks = pool.blocks + data
    _validate_pool(blocks, pool.type)
    pool.blocks = blocks
    pool.save()

    if pool.scope == FABRIC:
      # here, get unique list of fabric id's to extend pool entry with new blocks
        fabric_list = PoolEntry.objects.filter(pool_id=pool.id).exclude(fabric=None).values_list('fabric', flat=True).distinct()
        for fabric_id in fabric_list:
            fabric = Fabric.objects.get(pk=fabric_id)
            if pool.type == INTEGER:
                _create_integer_pool(pool, data, fabric)
            elif pool.type == IPV4:
                _create_ipv4_pool(pool, data, fabric)
            elif pool.type == IPV6:
                _create_ipv6_pool(pool, data, fabric)
        return pool

    if pool.type == INTEGER:
        _create_integer_pool(pool, data)
    elif pool.type == IPV4:
        _create_ipv4_pool(pool, data)
    elif pool.type == IPV6:
        _create_ipv6_pool(pool, data)

    return pool


def _validate_pool(blocks, data_type):
    num_blocks = len(blocks)

    for index in range(0, num_blocks):
        block = blocks[index]

        if data_type == INTEGER:
            start = int(block[START])
            end = int(block[END])

            if end < start:
                raise IgniteException(ERR_INV_POOL_RANGE)

            for inner_index in range(index + 1, num_blocks):
                curr_start = int(blocks[inner_index][START])
                curr_end = int(blocks[inner_index][END])

                if (start <= curr_start <= end or
                    start <= curr_end <= end or
                    curr_start <= start <= curr_end or
                    curr_start <= end <= curr_end):
                    raise IgniteException(ERR_POOL_RANGE_OVERLAP)

        elif data_type == IPV4 or data_type == IPV6:
            start = IPNetwork(block[START])
            end = IPNetwork(block[END])

            if start.prefixlen != end.prefixlen:
                raise IgniteException(ERR_MISMATCH_PREFIX_LEN)

            if index == 0:
                prefix = start.prefixlen
            else:
                if prefix != start.prefixlen:
                    raise IgniteException(ERR_MISMATCH_PREFIX_LEN_BLOCKS)

            if end.ip < start.ip:
                raise IgniteException(ERR_INV_POOL_RANGE)

            for inner_index in range(index + 1, num_blocks):
                curr_start = IPNetwork(blocks[inner_index][START])
                curr_end = IPNetwork(blocks[inner_index][END])

                if (start <= curr_start <= end or
                    start <= curr_end <= end or
                    curr_start <= start <= curr_end or
                    curr_start <= end <= curr_end):
                    raise IgniteException(ERR_POOL_RANGE_OVERLAP)


def _create_integer_pool(pool, blocks, fabric=None):
    for block in blocks:
        start = int(block[START])
        end = int(block[END])

        for value in range(start, end + 1):
            entry = PoolEntry()
            entry.pool = pool
            entry.fabric = fabric
            entry.value = str(value)
            entry.save()


def _create_ipv4_pool(pool, blocks, fabric=None):

    for block in blocks:
        start = IPNetwork(block[START])
        end = IPNetwork(block[END])

        for ip in range(start.ip, end.ip + 1):
            entry = PoolEntry()
            entry.pool = pool
            entry.fabric = fabric
            entry.value = str(IPAddress(ip)) + "/" + str(start.prefixlen)
            entry.save()


def _create_ipv6_pool(pool, blocks, fabric=None):

    for block in blocks:
        start = IPNetwork(block[START])
        end = IPNetwork(block[END])

        for ip in range(start.ip, end.ip + 1):
            entry = PoolEntry()
            entry.pool = pool
            entry.fabric = fabric
            entry.value = str(IPAddress(ip)) + "/" + str(start.prefixlen)
            entry.save()


def get_pool(id):
    pool = Pool.objects.get(pk=id)

    if pool.scope == GLOBAL:
        pool.entries = (PoolEntry.objects.filter(pool_id=pool.id).
                        exclude(switch=None))

        entry_list = list()

        for entry in pool.entries:
            entry.assigned = entry.switch.name
            entry_list.append(entry)

        pool.entries = entry_list

    return pool


def delete_pool(id):
    pool = Pool.objects.get(pk=id)

    if pool.ref_count:
        raise IgniteException(ERR_POOL_IN_USE)

    pool.delete()


def update_pool_ref_count(id, value):
    Pool.objects.filter(pk=id).update(ref_count=F('ref_count')+value)


def allocate_pool_entry(pool_id, switch_id, switch):
    logger.debug("pool id = %s, switch id = %s",
                 pool_id, switch_id)

    if not switch:
        switch = Switch.objects.get(pk=switch_id)

    pool = Pool.objects.get(pk=pool_id)

    if pool.scope == GLOBAL:
        fabric = None
    else:
        if not switch.topology:
            raise IgniteException(ERR_NON_FABRIC_POOL)

        fabric = Fabric.objects.get(pk=switch.topology.id)
        # check if fabric specific entries have been created
        entry = PoolEntry.objects.filter(pool=pool, fabric=fabric)

        if not entry:
            # create fabric specific entries
            if pool.type == INTEGER:
                _create_integer_pool(pool, pool.blocks, fabric)
            elif pool.type == IPV4:
                _create_ipv4_pool(pool, pool.blocks, fabric)
            elif pool.type == IPV6:
                _create_ipv6_pool(pool, pool.blocks, fabric)

    # check if pool entry has already been allocated to this switch
    try:
        entry = PoolEntry.objects.get(pool=pool, fabric=fabric,
                                      switch=switch)
        logger.debug("value = %s", entry.value)
        return entry.value
    except PoolEntry.DoesNotExist:
        pass

    # find new entry to allocate
    entries = PoolEntry.objects.filter(pool=pool, fabric=fabric, switch=None)

    if not entries:
        raise IgniteException(ERR_POOL_FULL)

    # save assigned switch in pool entry
    entry = entries.first()
    entry.switch = switch
    entry.save()
    logger.debug("value = %s", entry.value)
    return entry.value
