from django.db.models import F
import string

from constants import *
from models import Configlet
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def get_all_configlets(type):
    if type:
        return Configlet.objects.filter(type=type).order_by(NAME)

    return Configlet.objects.all().order_by(NAME)


def add_configlet(data, user):
    cfg = Configlet()
    cfg.name = data[NAME]
    cfg.group = data[GROUP]
    cfg.type = data[CONSTRUCT_TYPE]
    cfg.updated_by = user
    cfg.save()
    return cfg


def get_configlet(id):
    cfg = Configlet.objects.get(pk=id)

    cfg.file = []

    for line in cfg.path.file:
        cfg.file.append(string.rstrip(line))

    return cfg


def update_configlet(id, data, user):
    cfg = Configlet.objects.get(pk=id)
    cfg.path.delete(save=False)
    file_obj = data[FILE]
    cfg.path = file_obj
    file_content = file_obj.read()

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


def delete_configlet(id):
    cfg = Configlet.objects.get(pk=id)

    if cfg.ref_count:
        raise IgniteException(ERR_CFG_IN_USE)

    cfg.path.delete(save=False)
    cfg.delete()


def update_ref_count(id, value):
    Configlet.objects.filter(pk=id).update(ref_count=F('ref_count')+value)
