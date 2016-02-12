from mako.template import Template
import os
import subprocess
from django.db.models import ProtectedError


import configlet
from constants import *
import fabric
from ignite.settings import REPO_PATH
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

    if not data[CONSTRUCT_LIST]:
        raise IgniteException(ERR_PROF_IS_EMPTY)
    else:
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


def build_config_profile(cfg_list, switch):
    buff = ''
    param_value = {}
    construct_list = []

    for cfg in cfg_list:
        if cfg:
            construct_list += list(cfg.construct_list)

    for item in construct_list:

        cfglt = configlet.get_configlet(item[CONFIGLET_ID])
        buff += '\n!\n!%s config\n!\n' % cfglt.name
        mako_buff = ""
        construct_type = cfglt.type

        if construct_type == SCRIPT:
            logger.debug('Processing script %s' % cfglt.name)
        else:
            logger.debug('Processing configlet %s' % cfglt.name)

        mako_param_value = dict()

        for param_detail in item[PARAM_LIST]:
            value = None

            if param_detail[PARAM_TYPE] == VALUE:
                try:
                    value = param_value[param_detail[PARAM_VALUE]]
                except KeyError:
                    err_str = "%s %s" % (ERR_VALUE_NOT_FOUND,
                                         param_detail[PARAM_VALUE])
                    logger.error(err_str)
                    raise IgniteException(err_str)

            if param_detail[PARAM_TYPE] == FIXED:
                value = param_detail[PARAM_VALUE]

            if param_detail[PARAM_TYPE] == INSTANCE:
                value = fabric.build.get_instance_value(
                                            param_detail[PARAM_VALUE],
                                            switch,
                                            switch.name)

            if param_detail[PARAM_TYPE] == POOL:
                value = allocate_pool_entry(param_detail[PARAM_VALUE],
                                            switch.id,
                                            switch)

            if param_detail[PARAM_TYPE] == EVAL:
                try:
                    value = eval(param_detail[PARAM_VALUE])
                except SyntaxError:
                    raise IgniteException("%s = %s" % (ERR_EVAL_SYNTAX,
                                                       param_detail[PARAM_VALUE]))

            if value is None:
                err_str = "%s %s" % (ERR_VALUE_NOT_FOUND,
                                     param_detail[PARAM_NAME])
                logger.error(err_str)
                raise IgniteException(err_str)

            param_value[param_detail[PARAM_NAME]] = value

            if construct_type == SCRIPT:
                mako_param_name = PARAM_IDENTIFIER_SCRIPT +\
                                  param_detail[PARAM_NAME] +\
                                  PARAM_IDENTIFIER_SCRIPT
                mako_param_value[mako_param_name] = value

        for line in cfglt.path.file:
            logger.debug(line)

            if construct_type == SCRIPT:
                mako_buff += line
            else:
                param_list = parse_file(line, PARAM_EXP_CONFIGLET,
                                        PARAM_IDENTIFIER_CONFIGLET)

                for param in param_list:
                    logger.debug("Param to replace %s by value %s"
                                 % (param, param_value[param]))

                    line = line.replace(PARAM_IDENTIFIER_CONFIGLET + param +
                                        PARAM_IDENTIFIER_CONFIGLET,
                                        param_value[param])

                buff += line

        if mako_buff:
            buff += Template(mako_buff).render(**mako_param_value)

    return buff
