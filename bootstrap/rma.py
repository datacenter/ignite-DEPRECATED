from models import SwitchBootDetail
from fabric.models import Switch
from group.models import Group, GroupSwitch
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
        logger.debug("switch found with serial number : %s", old_serial_num)
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
            try:
                group_switches = GroupSwitch.objects.filter(grp_switch_id=switch.id).values_list('group_id', flat=True).distinct()
                for group_switch in group_switches:
                    group = Group.objects.get(pk=group_switch)
                    if group.ref_count>0:
                        logger.debug(ERR_SWITCH_IN_USE_JOB_SCHEDULE)
                        raise IgniteException(ERR_SWITCH_IN_USE_JOB_SCHEDULE)
            except GroupSwitch.DoesNotExist:
                pass
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

    switch = get_rma_switch(new_serial_num)
    if switch:
        logger.debug("Switch with serial number %s is already present. Can not assign same serial number to multiple switches", new_serial_num)
        raise IgniteException(ERR_NOT_ALLOWED_DUPLICATE_SERIAL + new_serial_num + 
                                 ERR_NOT_ALLOWED_DUPLICATE_SERIAL_CONTINUES + switch.topology.name)

    switch = get_rma_switch(old_serial_num)

    if switch:
        logger.debug("switch found with serial number:"+ old_serial_num)
        switch.serial_num = new_serial_num
        if switch.boot_detail:
            if switch.boot_detail.boot_status == BOOT_PROGRESS:
                logger.debug(ERR_SWITCH_BOOT_IN_PROGRESS)
                raise IgniteException(ERR_SWITCH_BOOT_IN_PROGRESS)
            else:
                boot_detail = switch.boot_detail
                switch.boot_detail = None

                if switch.topology:
                    logger.debug("switch is booted by matching into fabric")
                else:
                    logger.debug("switch is booted by matching into discovery_rule")
                    if switch.boot_detail.match_type == SERIAL_NUMBER:
                        updated = update_rma_rule(old_serial_num, new_serial_num,
                                                  id=switch.boot_detail.discovery_rule)
                    switch.name = new_serial_num

                switch.save()
                logger.debug("Serial number has been updated from %s to %s",old_serial_num, new_serial_num)
                logger.debug("Deleting boot details of switch")
                boot_detail.delete()
                logger.debug("boot details deleted")
                updated = True

        else:
            if switch.topology:
                switch.save()
                logger.debug("switch is present in fabric as not booted but build config is done")
                logger.debug("serial number has been updated from %s to %s",old_serial_num, new_serial_num)
                updated = True
            else:
                updated = update_rma_rule(old_serial_num, new_serial_num)
                switch.name = new_serial_num
                logger.debug("switch found as not booted and discovery rule also exist")
                switch.save()
                logger.debug("serial number has been updated from %s to %s",old_serial_num, new_serial_num)
                updated = True
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
            logger.debug(ERR_DISOVERY_RULE_EXIST)
            raise IgniteException(ERR_DISOVERY_RULE_EXIST)
    else:
        rule = find_dup_serial_discovery([old_serial_num], rma_case=True)

    if rule:
        rule.subrules = [r.replace(old_serial_num, new_serial_num) for r in rule.subrules]
        rule.save()
        logger.debug("Discovery rule found")
        return True
