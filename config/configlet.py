from django.db.models import F, Max
import hashlib
import os
import string

from constants import *
from ignite.settings import MEDIA_ROOT
from models import Configlet, ConfigletIndex
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_current_config_version(cfgindex_id):
    logger.debug(str(cfgindex_id))
    objs = Configlet.objects.filter(configletindex_id=cfgindex_id)
    ver = objs.aggregate(Max(VERSION))
    logger.debug(str(ver))
    if not ver['version__max']:
        raise IgniteException("Latest version not found")
    logger.debug("max version found is"+str(ver['version__max']))
    return ver['version__max']


def get_all_configlet_index(type):
    # get configlets with max version
    objects = ConfigletIndex.objects.all().order_by(NAME)
    cfgs = []
    for obj in objects:
        # to get max version configlet
        cur_ver = get_current_config_version(obj.id)
        if type:
            cfg = Configlet.objects.filter(configletindex_id=obj.id, version=cur_ver, type=type)
            if cfg:
                cfgs.append(cfg[0])
        else:
            cfgs.append(Configlet.objects.get(configletindex_id=obj.id, version=cur_ver))
    return cfgs


def add_configlet_index(data, user):
    cfgindex = ConfigletIndex()
    cfgindex.name = data[NAME]
    cfgindex.updated_by = user
    cfgindex.save()

    cfg = Configlet()
    cfg.name = data[NAME]
    cfg.version = 1
    cfg.group = data[GROUP]
    cfg.type = data[CONSTRUCT_TYPE]
    cfg.updated_by = user
    cfg.configletindex = cfgindex
    cfg.save()
    return cfg


def get_configlet_index(cfgindex_id):
    configs = Configlet.objects.filter(configletindex_id=cfgindex_id).order_by(VERSION)
    cfg_list = []
    for cfg in configs:
        cfg.file = []
        try:
            for line in cfg.path.file:
                cfg.file.append(string.rstrip(line))
            cfg_list.append(cfg)
        except IOError:
            raise IgniteException(ERR_CONFIGLET_FILE_NOT_FOUND+" : "+cfg.name)
    return cfg_list


def delete_configlet_index(cfgindex_id):
    logger.debug("delete configlet index " + str(cfgindex_id))
    configs = get_configlet_index(cfgindex_id)
    for config in configs:
        if config.ref_count:
            logger.error(ERR_CFG_IN_USE)
            raise IgniteException(ERR_CFG_IN_USE)
    ConfigletIndex.objects.filter(id=cfgindex_id).delete()


def get_configlet_byversion(cfgindex_id, version):
    cfgs = Configlet.objects.filter(configletindex_id=cfgindex_id, version=version)

    cfg = cfgs[0]
    cfg.file = []
    try:
        for line in cfg.path.file:
            cfg.file.append(string.rstrip(line))
        return cfg
    except IOError:
        raise IgniteException(ERR_CONFIGLET_FILE_NOT_FOUND+" : "+cfg.name)


def get_configlet(cfgindex_id, cfg_id):
    cfg = Configlet.objects.get(pk=cfg_id, configletindex_id=cfgindex_id)

    cfg.file = []
    try:
        for line in cfg.path.file:
            cfg.file.append(string.rstrip(line))
        return cfg
    except IOError:
        raise IgniteException(ERR_CONFIGLET_FILE_NOT_FOUND+" : "+cfg.name)


def update_configlet(cfgindex_id, fileobject, cfg_id=0, new_version=None,  user=''):
    cfg = None
    current_version = get_current_config_version(cfgindex_id)
    logger.debug("current version " + str(current_version))
    cfg = Configlet.objects.get(configletindex_id=cfgindex_id, version=current_version)
    if cfg_id:
        logger.debug(str(cfg.id))
        logger.debug(str(cfg_id))
        if cfg_id != cfg.id:
            err = "Requested configlet is not latest version(%s)" % (str(cfg_id))
            logger.error(err)
            raise IgniteException(err)

        cfg = Configlet.objects.get(pk=cfg_id, configletindex_id=cfgindex_id)
    file_obj = fileobject[FILE]
    file_content = file_obj.read()
    if cfg.path and cfg_id:
        logger.debug(str(cfg.path))
        try:
            old = hashlib.md5(open(os.path.join(MEDIA_ROOT, str(cfg.path)), 'rb').read()).hexdigest()
            logger.debug("existed configlet md5= " + old)
            logger.debug(str(old))
            new = hashlib.md5(file_content).hexdigest()
            logger.debug("User given  configlet md5= " + new)
            change = False
            params = None
            logger.debug(str(new))
            if old == new:
                return cfg
            if cfg.type == SCRIPT:
                params = parse_file(file_content, PARAM_EXP_SCRIPT,
                                    PARAM_IDENTIFIER_SCRIPT)
            else:
                params = parse_file(file_content, PARAM_EXP_CONFIGLET,
                                    PARAM_IDENTIFIER_CONFIGLET)
            logger.debug("new parameters " + str(params))
            logger.debug("old parameters " + str(cfg.parameters))
            if params != cfg.parameters:
                change = True
            if change:
                logger.error(ERR_CHANGE_IN_PARAMS)
                raise IgniteException(ERR_CHANGE_IN_PARAMS)
            else:
                logger.debug("new version boolean is " + new_version)
                if str(new_version) in ['true', 'True']:
                    logger.debug("User requested new version of configlet")
                    new_cfg = Configlet()
                    new_cfg.name = cfg.name
                    new_cfg.updated_by = user
                    new_cfg.group = cfg.group
                    new_cfg.type = cfg.type
                    new_cfg.parameters = params
                    new_cfg.configletindex = cfg.configletindex
                    new_cfg.save()
                    new_cfg.version = current_version + 1
                    new_cfg.path.delete(save=False)
                    new_cfg.path = file_obj
                    new_cfg.save()
                    logger.debug("File content: "+str(file_content))
                    logger.debug("File named %s saved in db" % (file_obj))
                    return new_cfg
                elif str(new_version) in ['false', 'False']:
                    cfg.path.delete(save=False)
                    cfg.path = file_obj
                    cfg.updated_by = user
                    cfg.save()
                    logger.debug("File content: "+str(file_content))
                    logger.debug("File named %s saved in db" % (file_obj))
                    return cfg
                else:
                    err = "Unknown version type-" + str(new_version)
                    logger.error(err)
                    raise IgniteException(err)

        except Exception as e:
            logger.error(e)
            raise IgniteException(str(e))
    if cfg.path:
        err = "Update/Newversion is not possible on this request"
        logger.error(err)
        raise IgniteException(err)
    cfg.path.delete(save=False)
    cfg.path = file_obj

    logger.debug("adding a new configlet")
    if cfg.type == SCRIPT:
        params = parse_file(file_content, PARAM_EXP_SCRIPT,
                            PARAM_IDENTIFIER_SCRIPT)
    else:
        params = parse_file(file_content, PARAM_EXP_CONFIGLET,
                            PARAM_IDENTIFIER_CONFIGLET)

    cfg.parameters = params
    cfg.updated_by = user
    cfg.save()
    logger.debug("File content: "+str(file_content))
    logger.debug("File named %s saved in db" % (file_obj))
    return cfg


def delete_configlet(cfgindex_id, cfg_id):
    logger.debug(str(cfgindex_id))
    logger.debug(str(cfg_id))
    cfg = Configlet.objects.get(pk=cfg_id, configletindex_id=cfgindex_id)
    current_version = get_current_config_version(cfgindex_id)
    if int(current_version) == 1:
        err = "This is the Basic version(1), can't be deleted from here"
        logger.error(err)
        raise IgniteException(err)
    logger.debug("current_version - " + str(current_version))
    cfg_latest = Configlet.objects.get(configletindex_id=cfgindex_id, version=current_version)
    if cfg_id != cfg_latest.id:
        err = "Requested configlet is not latest version(%s)" % (str(cfg_id))
        logger.error(err)
        raise IgniteException(err)

    if cfg.ref_count:
        raise IgniteException(ERR_CFG_IN_USE)

    cfg.path.delete(save=False)
    cfg.delete()


def update_ref_count(cfgindex_id, version,  value):
    Configlet.objects.filter(configletindex_id=cfgindex_id, version=version).update(ref_count=F('ref_count')+value)
