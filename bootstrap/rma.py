from models import SwitchBootDetail
from fabric.models import Switch
from constants import *
from discovery.discoveryrule import find_dup_serial_discovery
from discovery.models import DiscoveryRule
from fabric.constants import NEIGHBOR, SERIAL_NUMBER
from serializers import BootstrapSwitchSerializer
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_rma_switch(old_serial_num):
    try:
        switch = Switch.objects.get(serial_num=old_serial_num)
        logger.debug("switch found")
        return switch
    except Switch.DoesNotExist:
        return None


def get_rma_detail(old_serial_num):
    #check if switch exist with the searched serial number
    switch = get_rma_switch(old_serial_num)
    if switch:
        switch.match = SWITCH
        switch.switch_detail = switch
        if switch.boot_detail:
            #booting of switch is in progress
            if switch.boot_detail.boot_status == BOOT_PROGRESS:
                logger.debug(ERR_SWITCH_BOOT_IN_PROGRESS)
                raise IgniteException(ERR_SWITCH_BOOT_IN_PROGRESS)
        else:
            rule = find_dup_serial_discovery([old_serial_num], rma_case=True)
            if rule:
                switch.rule = rule.id
                logger.debug("switch found as not booted and discovery rule also exist")
        return switch
    return None


def get_rma_rule(sn):
    #check if rule exist
    rule = find_dup_serial_discovery([sn], rma_case=True)
    if rule:
        rule.match = RULE
        rule.rule = rule.id
        logger.debug("switch does not exist with searched serial number but discovery rule exist")
        return rule
    return None


def update_rma_detail(data):
    updated = False
    old_serial_num = data[OLD_SERIAL_NUM]
    new_serial_num = data[NEW_SERIAL_NUM]
    switch = get_rma_switch(old_serial_num)

    if switch:
        logger.debug("switch found")
        switch.serial_num = new_serial_num
        if switch.boot_detail:
            if switch.boot_detail.boot_status == BOOT_PROGRESS:
                logger.debug(ERR_SWITCH_BOOT_IN_PROGRESS)
                raise IgniteException(ERR_SWITCH_BOOT_IN_PROGRESS)
            else:
                if switch.topology:
                    switch.boot_detail.match_type = ""
                    switch.boot_detail.boot_status = None
                    switch.boot_detail.discovery_rule = 0
                    switch.boot_detail.serial_number = ""
                    switch.boot_detail.boot_time = None
                    switch.boot_detail.save()
                    switch.save()
                    logger.debug("switch is booted by matching into fabric")
                else:
                    if switch.boot_detail.match_type == SERIAL_NUMBER:
                        updated = update_rma_rule(old_serial_num, new_serial_num, id=switch.boot_detail.discovery_rule)
                    boot_detail = switch.boot_detail
                    switch.boot_detail = None
                    switch.name = new_serial_num
                    switch.save()
                    boot_detail.delete()
                    logger.debug("switch is booted by matching into discovery_rule")
                updated = True

        else:
            if switch.topology:
                switch.save()
                updated = True
                logger.debug("switch is present in fabric as not booted but build config is done")
            else:
                updated = update_rma_rule(old_serial_num, new_serial_num)
                switch.name = new_serial_num
                switch.save()
                updated = True
                logger.debug("switch found as not booted and discovery rule also exist")
    else:
        updated = update_rma_rule(old_serial_num, new_serial_num)

    if not updated:
        logger.debug(ERR_SERIAL_NOT_FOUND)
        raise IgniteException(ERR_SERIAL_NOT_FOUND)


def update_rma_rule(old_serial_num, new_serial_num, id=0):
    if id:
        try:
            rule = DiscoveryRule.objects.get(id=id)
        except DiscoveryRule.DoesNotExist:
            raise IgniteException(ERR_DISOVERY_RULE_EXIST)
    else:
        rule = find_dup_serial_discovery([old_serial_num], rma_case=True)

    if rule:
        rule.subrules = [r.replace(old_serial_num, new_serial_num) for r in rule.subrules]
        rule.save()
        logger.debug("Discovery rule found")
        return True
