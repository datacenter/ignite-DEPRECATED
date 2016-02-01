import ast
from collections import Counter
import json
import re
import random

from config.profile import get_profile
from constants import *
from fabric.models import Switch
from models import DiscoveryRule
from serializer import DiscoveryRuleSerializer, DiscoveryRuleGetSerializer
from serializer import DiscoveryRuleGetDetailSerializer
from utils.exception import IgniteException
from workflow.workflow import get_workflow
import image.image_profile as image_profile

import logging
logger = logging.getLogger(__name__)


def find_repeat_serial_num(serial_num_list):
    dup_items = [k for k, v in Counter(serial_num_list).items() if v > 1]
    if len(dup_items) > 0:
        raise IgniteException(ERR_SERIAL_REPEATED)
    return


def find_dup_serial_discovery(serial_list, rule_id=0):
    rules = None
    if rule_id:
        rules = DiscoveryRule.objects.exclude(id=rule_id
                                              ).filter(match=SERIAL_NUM)
    else:
        rules = DiscoveryRule.objects.all().filter(match=SERIAL_NUM)
    if rules is None:
        return

    for serial in serial_list:
        for rule in rules:
            if str(serial) in rule.subrules:
                msg = serial + ERR_SERIAL_EXISTS_DISRULES + rule.name
                raise IgniteException(msg)
    return True


def find_duplicate(serial_list, rule_id=0):
    find_dup_serial_discovery(serial_list, rule_id)

    switches = Switch.objects.values_list('serial_num',
                                          flat=True).exclude(serial_num='')
    for serial in serial_list:
        if str(serial) in switches:
            msg = serial + ERR_SERIAL_EXISTS_FABRIC
            raise IgniteException(msg)


def get_all_discoveryrules():
    return DiscoveryRule.objects.all()


def get_discoveryrule(id):
    return DiscoveryRule.objects.get(pk=id)


def add_discoveryrule(data, username):
    config_obj = get_profile(data[CONFIG])
    image = image_profile.get_profile(data[IMAGE])
    rule_object = DiscoveryRule()
    if data[WORKFLOW]:
        wf = get_workflow(data[WORKFLOW])
        rule_object.workflow = wf
    rule_object.name = data[NAME]
    rule_object.match = data[MATCH].lower()
    if str(data[MATCH]) == SERIAL_NUM:
        find_repeat_serial_num(data[SUBRULES])
        find_duplicate(data[SUBRULES])
    rule_object.priority = data[PRIORITY]
    rule_object.config = config_obj
    rule_object.image = image
    rule_object.subrules = data[SUBRULES]
    rule_object.updated_by = username
    rule_object.save()
    return rule_object


def update_discoveryrule(id, data, username):
    config_obj = get_profile(data[CONFIG])
    image = image_profile.get_profile(data[IMAGE])
    rule_object = get_discoveryrule(id)
    if data[WORKFLOW]:
        wf = get_workflow(data[WORKFLOW])
        rule_object.workflow = wf
    else:
        rule_object.workflow = None
    rule_object.name = data[NAME]
    rule_object.match = data[MATCH].lower()
    if str(data[MATCH]) == SERIAL_NUM:
        find_repeat_serial_num(data[SUBRULES])
        find_duplicate(data[SUBRULES], rule_id=id)
    rule_object.priority = data[PRIORITY]
    rule_object.config = config_obj
    rule_object.image = image
    rule_object.subrules = data[SUBRULES]
    rule_object.updated_by = username
    rule_object.save()
    return rule_object


def delete_discoveryrule(id):
    DiscoveryRule.objects.filter(pk=id).delete()


def regex_match(condition, string, value):
    if condition == CONTAIN:
        if re.search(string, value) is None:
            return 0
        return 1
    if condition == NO_CONTAIN:
        if re.search(string, value) is None:
            return 1
        return 0
    if condition == MATCH:
        string = '^' + string + '$'
        if re.search(string, value) is None:
            return 0
        return 1
    if condition == NO_MATCH:
        string = '^' + string + '$'
        if re.search(string, value) is None:
            return 1
        return 0
    if condition == ANY:
        return 1
    return 1


def match_discovery_rules(cdp_nei_list):
    neighbor_list = cdp_nei_list[NEIGH_LIST]
    discoveryrule = DiscoveryRule.objects.exclude(match=SERIAL_NUM
                                                  ).order_by(PRIORITY)
    matched_dis_obj = None
    config_id = None

    if len(neighbor_list) > 0:
        for single_obj in discoveryrule.iterator():
            subrules_list = single_obj.subrules
            all_subrule_match_flag = 0
            for subrule in subrules_list:
                subrule_match_flag = 0

                for neigh in neighbor_list:
                    if(regex_match(subrule[RN_CONDITION],
                                   subrule[RN_STR], neigh[REMOTE_NODE])):
                        if(regex_match(subrule[RP_CONDITION],
                                       subrule[RP_STR],
                                       neigh[REMOTE_PORT])):
                            if(regex_match(subrule[LP_CONDITION],
                                           subrule[LP_STR],
                                           neigh[LOCAL_PORT])):
                                subrule_match_flag = 1
                                logger.debug("Matched a neighbor_list" +
                                             str(neigh) + " with subrule " + str(subrule))
                                break

                if single_obj.match == ALL:
                    if subrule_match_flag == 0:
                        all_subrule_match_flag = 0
                        break
                    else:
                        all_subrule_match_flag = 1
                elif single_obj.match == ANY:
                    if subrule_match_flag == 1:
                        all_subrule_match_flag = 1
                        break
            if all_subrule_match_flag == 1:
                config_id = single_obj.config.id
                matched_dis_obj = single_obj
                logger.debug("The matching discoveryrule id is: "
                             + str(single_obj.id))
                break

    if config_id is None:
        discoveryrule = DiscoveryRule.objects.filter(match=SERIAL_NUM
                                                     ).order_by(PRIORITY)
        serial_id = cdp_nei_list[SERIAL_NUM]
        for single_obj in discoveryrule.iterator():
            #subrules_list = ast.literal_eval(single_obj.subrules)
            for subrule_serial_id in single_obj.subrules:
                if serial_id == subrule_serial_id:
                    config_id = single_obj.config.id
                    matched_dis_obj = single_obj
                    logger.debug("The matching discoveryrule with serial-id is: " + str(single_obj.id))
                    break
            if config_id is not None:
                break
    logger.debug("The configuration id is: " + str(config_id))

    return matched_dis_obj
