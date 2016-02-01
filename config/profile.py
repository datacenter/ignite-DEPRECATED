from django.db.models import ProtectedError

import configlet
from constants import *
import fabric
from models import Configlet, Profile
from pool.pool import allocate_pool_entry, update_pool_ref_count
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_all_profiles(submit):
    if submit == TRUE:
        return Profile.objects.filter(submit=True).order_by(NAME)
    elif submit == FALSE:
        return Profile.objects.filter(submit=False).order_by(NAME)
    else:
        return Profile.objects.all().order_by(NAME)


def add_profile(data, user):
    return _add_profile(data, user)


def _add_profile(data, user, id=0):
    logger.debug("profile name = %s", data[NAME])

    if id:
        # get existing profile
        profile = Profile.objects.get(pk=id)

        for cfg in profile.construct_list:
            configlet.update_ref_count(cfg[CONFIGLET_ID], -1)
            for param_detail in cfg[PARAM_LIST]:
                if param_detail[PARAM_TYPE] == POOL:
                    update_pool_ref_count(int(param_detail[PARAM_VALUE]), -1)

    else:
        # create new profile
        profile = Profile()

    profile.name = data[NAME]
    profile.submit = data[SUBMIT]
    profile.construct_list = data[CONSTRUCT_LIST]
    profile.updated_by = user
    profile.save()

    # increment ref count of configlets and pool used in this profile
    for cfg in profile.construct_list:
        configlet.update_ref_count(cfg[CONFIGLET_ID], 1)
        for param_detail in cfg[PARAM_LIST]:
            if param_detail[PARAM_TYPE] == POOL:
                update_pool_ref_count(int(param_detail[PARAM_VALUE]), 1)

    return profile


def get_profile(id):
    return Profile.objects.get(pk=id)


def update_profile(id, data, user):
    return _add_profile(data, user, id)


def delete_profile(id):
    profile = Profile.objects.get(pk=id)

    # decrement ref count of configlets used in this profile
    for cfg in profile.construct_list:
        configlet.update_ref_count(cfg[CONFIGLET_ID], -1)
        for param_detail in cfg[PARAM_LIST]:
            if param_detail[PARAM_TYPE] == POOL:
                update_pool_ref_count(int(param_detail[PARAM_VALUE]), -1)
    try:
        profile.delete()
    except ProtectedError:
        raise IgniteException(ERR_PROF_IN_USE)


def build_config_profile(cfg, switch):
    buff = ''
    param_value = {}

    for item in cfg.construct_list:
        cfglt = configlet.get_configlet(item[CONFIGLET_ID])
        logger.debug('Processing configlet %s' % cfglt.name)
        buff += '\n!\n!%s config\n!\n\n' % cfglt.name

        for param_detail in item[PARAM_LIST]:
            value = None

            if param_detail[PARAM_TYPE] == VALUE:
                try:
                    value = param_value[param_detail[PARAM_VALUE]]
                except KeyError:
                    err_str = "%s %s" % (ERR_VALUE_NOT_FOUND,
                                         param_detail[PARAM_VALUE])
                    logger.error(err_str)
                    raise IgniteException

            if param_detail[PARAM_TYPE] == FIXED:
                value = param_detail[PARAM_VALUE]

            if param_detail[PARAM_TYPE] == INSTANCE:
                value = fabric.build.get_instance_value(
                                            param_detail[PARAM_NAME],
                                            switch,
                                            switch.name)

            if param_detail[PARAM_TYPE] == POOL:
                value = allocate_pool_entry(param_detail[PARAM_VALUE],
                                            switch.id,
                                            switch)

            if value is None:
                err_str = "%s %s" % (ERR_VALUE_NOT_FOUND,
                                     param_detail[PARAM_NAME])
                logger.error(err_str)
                raise IgniteException(err_str)

            param_value[param_detail[PARAM_NAME]] = value

        for line in cfglt.path.file:
            param_list = parse_file(line)

            for param in param_list:
                line = line.replace('$$' + param + '$$', param_value[param])

            buff += line

    return buff
