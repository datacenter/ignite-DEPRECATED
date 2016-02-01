from django.db import transaction

import configlet
from constants import *
from models import Configlet, Profile
import profile
from serializer import *
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_configlets():
    cfgs = configlet.get_all_configlets()
    serializer = ConfigletBriefSerializer(cfgs, many=True)
    return serializer.data


@transaction.atomic
def add_configlet(data, username=''):
    serializer = ConfigletPostSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    cfg = configlet.add_configlet(serializer.data, username)
    serializer = ConfigletBriefSerializer(cfg)
    return serializer.data


def get_configlet(id):
    cfg = configlet.get_configlet(id)
    serializer = ConfigletSerializer(cfg)
    return serializer.data


@transaction.atomic
def update_configlet(id, data, username=''):
    cfg = configlet.update_configlet(id, data, username)
    serializer = ConfigletBriefSerializer(cfg)
    return serializer.data


@transaction.atomic
def delete_configlet(id):
    configlet.delete_configlet(id)


def get_all_profiles(submit):
    profiles = profile.get_all_profiles(submit)
    serializer = ProfileBriefSerializer(profiles, many=True)
    return serializer.data


@transaction.atomic
def add_profile(data, username=''):
    serializer = ProfileSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    prof = profile.add_profile(serializer.data, username)
    serializer = ProfileSerializer(prof)
    return serializer.data


def get_profile(id):
    serializer = ProfileSerializer(profile.get_profile(id))
    return serializer.data


@transaction.atomic
def update_profile(id, data, username=''):
    serializer = ProfileSerializer(data=data)

    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    prof = profile.update_profile(id, serializer.data, username)
    serializer = ProfileSerializer(prof)
    return serializer.data


@transaction.atomic
def delete_profile(id):
    profile.delete_profile(id)
