from mako.template import Template
import json
import os
import subprocess
from django.db.models import Max, ProtectedError


import configlet
from constants import *
import fabric
from ignite.settings import REPO_PATH
from models import Configlet, Profile, ProfileIndex
from pool.pool import allocate_pool_entry, update_pool_ref_count
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_profile_current_version(prindex_id):
    objs = Profile.objects.filter(profileindex_id=prindex_id)
    ver = objs.aggregate(Max(VERSION))
    if not ver['version__max']:
        raise IgniteException("Latest version not found")
    logger.debug("max version found is"+str(ver['version__max']))
    return ver['version__max']


def get_all_profile_index(submit):
    pr_index = ProfileIndex.objects.all().order_by(NAME)
    profiles = []
    for pr in pr_index:
        current_version = get_profile_current_version(pr.id)
        if submit == TRUE:
            profiles += Profile.objects.filter(profileindex=pr.id, version=current_version, submit=True)
        elif submit == FALSE:
            profiles += Profile.objects.filter(profileindex=pr.id, version=current_version, submit=False)
        else:
            profiles += Profile.objects.filter(profileindex=pr.id, version=current_version)
    return profiles


def add_profile_index(data, user):
    return _add_profile_index(data, user)


def _add_profile_index(data, user, prindex_id=0, pr_id=0):
    logger.debug("profile name = %s", data[NAME])
    import hashlib

    pr_index = None
    profile = None
    temp1 = json.dumps(data[CONSTRUCT_LIST])

    if pr_id and prindex_id:
        # get existing profile
        pr_index = ProfileIndex.objects.get(pk=prindex_id)
        profile = Profile.objects.get(pk=pr_id, profileindex_id=prindex_id)
        current_version = get_profile_current_version(prindex_id)
        new = hashlib.md5(str(json.loads(temp1))).hexdigest()
        old = hashlib.md5(str(profile.construct_list)).hexdigest()

        if not data[CONSTRUCT_LIST]:
            raise IgniteException(ERR_PROF_IS_EMPTY)

        if old == new:
            if not profile.submit:
                profile.submit = data[SUBMIT]
                profile.save()
            return profile

        obj = Profile.objects.get(profileindex=prindex_id, version=current_version)
        if obj.id != pr_id:
            err = "Update/Newversion can only be done with latest version of config profile"
            logger.error(err)
            raise IgniteException(err)

        for cfg in profile.construct_list:
            configlet.update_ref_count(cfg[CONFIGLETINDEX_ID], cfg[VERSION], -1)
            for param_detail in cfg[PARAM_LIST]:
                if param_detail[PARAM_TYPE] == POOL:
                    update_pool_ref_count(int(param_detail[PARAM_VALUE]), -1)

        if data[NEW_VERSION]:
            if not profile.submit:
                err = "Please submit current version, then create new version"
                logger.error(err)
                raise IgniteException(err)

            profile = Profile()
            profile.version = current_version + 1
        else:
            profile = Profile.objects.get(pk=pr_id)
    else:
        # create new profile
        if not data[CONSTRUCT_LIST]:
            raise IgniteException(ERR_PROF_IS_EMPTY)
        pr_index = ProfileIndex()
        pr_index.name = data[NAME]
        pr_index.updated_by = user
        pr_index.save()

        profile = Profile()
        profile.version = 1

    profile.name = data[NAME]
    profile.construct_list = data[CONSTRUCT_LIST]
    profile.submit = data[SUBMIT]
    profile.updated_by = user
    profile.profileindex = pr_index
    profile.save()

    # increment ref count of configlets and pool used in this profile
    for cfg in profile.construct_list:
        configlet.update_ref_count(cfg[CONFIGLETINDEX_ID], cfg[VERSION],  1)
        for param_detail in cfg[PARAM_LIST]:
            if param_detail[PARAM_TYPE] == POOL:
                update_pool_ref_count(int(param_detail[PARAM_VALUE]), 1)

    return profile


def get_profile_index(prindex_id):
    return Profile.objects.filter(profileindex_id=prindex_id).order_by(VERSION)


def delete_profile_index(prindex_id):
    pr_index = ProfileIndex.objects.get(pk=prindex_id)
    profiles = Profile.objects.filter(profileindex_id=prindex_id)

    # decrement ref count of configlets used in this profile
    for pr in profiles:
        for cfg in pr.construct_list:
            configlet.update_ref_count(cfg[CONFIGLETINDEX_ID], cfg[VERSION], -1)
            for param_detail in cfg[PARAM_LIST]:
                if param_detail[PARAM_TYPE] == POOL:
                    update_pool_ref_count(int(param_detail[PARAM_VALUE]), -1)
        try:
            pr.delete()
        except ProtectedError:
            raise IgniteException(ERR_PROF_IN_USE)
    pr_index.delete()


def get_profile_by_index(prindex_id, pr_id):
    return Profile.objects.get(pk=pr_id, profileindex_id=prindex_id)


def get_profile(pr_id):
    return Profile.objects.get(pk=pr_id)


def update_profile(prindex_id, pr_id, data, username=''):
    return _add_profile_index(data, username, prindex_id, pr_id)


def delete_profile(prindex_id, pr_id):
    pr = get_profile_by_index(prindex_id, pr_id)
    current_version = get_profile_current_version(prindex_id)
    obj = Profile.objects.get(profileindex=prindex_id, version=current_version)
    if int(current_version) == 1:
        err = "This is the Basic version(1), can't be deleted from here"
        logger.error(err)
        raise IgniteException(err)
    if obj.id != pr_id:
        err = "Update/Newversion can only be done with latest version of config profile"
        logger.error(err)
        raise IgniteException(err)

    for cfg in pr.construct_list:
        configlet.update_ref_count(cfg[CONFIGLETINDEX_ID], cfg[VERSION], -1)
        for param_detail in cfg[PARAM_LIST]:
            if param_detail[PARAM_TYPE] == POOL:
                update_pool_ref_count(int(param_detail[PARAM_VALUE]), -1)
    try:
        pr.delete()
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

        cfglt = configlet.get_configlet_byversion(item[CONFIGLETINDEX_ID], item[VERSION])
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


def get_all_profiles():
    prof = Profile.objects.all().filter(submit=True)
    return prof
