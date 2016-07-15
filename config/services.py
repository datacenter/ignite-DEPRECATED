from django.db import transaction

import configlet
from constants import *
from models import ConfigletIndex, Configlet, Profile, ProfileIndex
import profile
from serializer import *
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_configlet_index(type):
    cfgs = configlet.get_all_configlet_index(type)
    serializer = ConfigletBriefSerializer(cfgs, many=True)
    return serializer.data


@transaction.atomic
def add_configlet_index(data, username=''):
    serializer = ConfigletPostSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    cfg = configlet.add_configlet_index(serializer.data, username)
    serializer = ConfigletBriefSerializer(cfg)
    return serializer.data


def get_configlet_index(cfgindex_id):
    cfgs = configlet.get_configlet_index(cfgindex_id)
    serializer = ConfigletSerializer(cfgs, many=True)
    return serializer.data


@transaction.atomic
def delete_configlet_index(cfgindex_id):
    configlet.delete_configlet_index(cfgindex_id)


def get_configlet(cfgindex_id, cfg_id):
    cfg = configlet.get_configlet(cfgindex_id, cfg_id)
    serializer = ConfigletSerializer(cfg)
    return serializer.data


@transaction.atomic
def update_configlet_index(cfgindex_id, fileobject, new_version, username=''):
    cfg_id = 0
    cfg = configlet.update_configlet(cfgindex_id, fileobject, cfg_id, new_version, username)
    serializer = ConfigletBriefSerializer(cfg)
    return serializer.data


@transaction.atomic
def update_configlet(cfgindex_id, fileobject, cfg_id, new_version, username=''):
    cfg = configlet.update_configlet(cfgindex_id, fileobject, cfg_id, new_version, username)
    serializer = ConfigletBriefSerializer(cfg)
    return serializer.data


@transaction.atomic
def delete_configlet(cfgindex_id, cfg_id):
    configlet.delete_configlet(cfgindex_id, cfg_id)


def get_all_profile_index(submit):
    profiles = profile.get_all_profile_index(submit)
    serializer = ProfileBriefSerializer(profiles, many=True)
    return serializer.data


@transaction.atomic
def add_profile_index(data, username=''):
    serializer = ProfilePostSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    prof = profile.add_profile_index(serializer.data, username)
    serializer = ProfileSerializer(prof)
    return serializer.data


def get_profile_index(prindex_id):
    profs = profile.get_profile_index(prindex_id)
    serializer = ProfileSerializer(profs, many=True)
    return serializer.data


@transaction.atomic
def delete_profile_index(prindex_id):
    profile.delete_profile_index(prindex_id)


def get_profile_by_index(prindex_id, pr_id):
    prof = profile.get_profile_by_index(prindex_id, pr_id)
    serializer = ProfileSerializer(prof)
    return serializer.data


@transaction.atomic
def update_profile(prindex_id, pr_id, data, username=''):
    if pr_id == 1:
        raise IgniteException(ERR_CAN_NOT_EDIT_DEFAULT_CONFIG)

    serializer = ProfilePostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    prof = profile.update_profile(prindex_id, pr_id, serializer.data, username)
    serializer = ProfileSerializer(prof)
    return serializer.data


@transaction.atomic
def delete_profile(prindex_id, pr_id):
    if pr_id == 1:
        raise IgniteException(ERR_CAN_NOT_DELETE_DEFAULT_CONFIG)
    profile.delete_profile(prindex_id, pr_id)


def get_all_profiles():
    prof = profile.get_all_profiles()
    serializer = AllProfilesSerializer(prof, many=True)
    return serializer.data
