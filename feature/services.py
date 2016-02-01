from django.db import transaction
from utils.exception import IgniteException

from serializers import *
from constants import *
import string
import feature
import logging

logger = logging.getLogger(__name__)


def get_all_features():
    obj_ls = feature.get_all_features()
    serializer = FeatureGetBriefSerializer(obj_ls, many=True)
    return serializer.data


@transaction.atomic
def add_feature(data, username=''):
    serializer = FeatureSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    feature_obj = feature.add_feature(data, username)
    serializer = FeatureGetBriefSerializer(feature_obj)
    return serializer.data


def get_feature(id):
    feature_obj = feature.get_feature(id)
    serializer = FeatureGetSerializer(feature_obj)
    return serializer.data


@transaction.atomic
def update_feature(id, data, username=''):
    feature_obj = feature.update_feature(id, data, username)
    serializer = FeatureGetBriefSerializer(feature_obj)
    return serializer.data


@transaction.atomic
def delete_feature(id):
    feature.delete_feature(id)


def get_all_profiles(submit):
    objects = feature.get_all_profiles(submit)
    serializer = ProfileGetAllSerializer(objects, many=True)
    return serializer.data


@transaction.atomic
def add_profile(data, username=''):
    serializer = ProfileSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    obj = feature.add_profile(data, username)
    serializer = ProfileGetSerializer(obj)
    return serializer.data


def get_profile(id):
    obj = feature.get_profile(id)
    serializer = ProfileGetSerializer(obj)
    return serializer.data


@transaction.atomic
def update_profile(id, data, username=''):
    serializer = ProfileSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    obj = feature.update_profile(id, data, username)
    serializer = ProfileGetSerializer(obj)
    return serializer.data


@transaction.atomic
def delete_profile(id):
    feature.delete_profile(id)
