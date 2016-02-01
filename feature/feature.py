from django.db.models import ProtectedError
import json
import string

from constants import *
from models import Feature, Profile
from utils.exception import IgniteException
from utils.utils import parse_file

import logging
logger = logging.getLogger(__name__)


def update_ref_count(data, value):
    for obj in data:
        feature = Feature.objects.get(pk=obj[TEMPLATE_ID])
        feature.ref_count = feature.ref_count + value
        feature.save()


def get_all_features():
    feature_objs = Feature.objects.order_by(NAME)
    logger.debug("Total fetures found: "+str(len(feature_objs)))
    return feature_objs


def add_feature(data, user):
    feature = Feature()
    feature.name = data[NAME]
    feature.group = data[GROUP]
    feature.updated_by = user
    feature.save()
    return feature


def get_feature(id):
    obj = Feature.objects.get(pk=id)
    obj.file = []
    for line in obj.path.file:
        obj.file.append(string.rstrip(line))
    return obj


def update_feature(id, data, user):
    feature_obj = Feature.objects.get(pk=id)
    feature_obj.path.delete(save=False)
    file_obj = data[FILE]
    feature_obj.path = file_obj
    file_content = file_obj.read()
    params = parse_file(file_content)
    feature_obj.parameters = params
    feature_obj.updated_by = user
    feature_obj.save()
    return feature_obj


def delete_feature(id):
    feature = Feature.objects.get(pk=id)
    if feature.ref_count:
        raise IgniteException(ERR_FEAT_IN_USE)
    feature.path.delete(save=False)
    feature.delete()


def get_all_profiles(submit):
    if submit == TRUE:
        return Profile.objects.filter(submit=True).order_by(NAME)
    elif submit == FALSE:
        return Profile.objects.filter(submit=False).order_by(NAME)
    else:
        return Profile.objects.all().order_by(NAME)


def add_profile(data, user):
    return _add_profile(data, user=user)


def get_profile(id):
    return Profile.objects.get(pk=id)


def update_profile(id, data, user):
    return _add_profile(data, user, id=id)


def _add_profile(data, user, id=0):
    if id:
        obj = get_profile(id)
        update_ref_count(obj.construct_list, -1)
        obj.name = data[NAME]
        obj.construct_list = data[CONSTRUCT_LIST]
        obj.submit = data[SUBMIT]
        obj.updated_by = user
        update_ref_count(data[CONSTRUCT_LIST], +1)
        obj.save()
        return obj
    else:
        fp_object = Profile()
        fp_object.name = data[NAME]
        fp_object.construct_list = data[CONSTRUCT_LIST]
        fp_object.submit = data[SUBMIT]
        fp_object.updated_by = user
        update_ref_count(data[CONSTRUCT_LIST], +1)
        fp_object.save()
        return fp_object


def delete_profile(id):
    obj = Profile.objects.get(pk=id)
    update_ref_count(obj.construct_list, -1)

    try:
        obj.delete()
    except ProtectedError:
        raise IgniteException(ERR_PROF_IN_USE)


def build_feature_profile(feature_prof):
    buff = '{'
    configs = {}

    for item in feature_prof.construct_list:
        configs = {}
        feat = get_feature(item[TEMPLATE_ID])

        for line in feat.path.file:

            for param_detail in item[PARAM_LIST]:
                line = line.replace('$$' + param_detail[PARAM_NAME] + '$$',
                                    param_detail[PARAM_VALUE])

            logger.debug(line)
            buff += line

        buff += ','

    buff = buff[:-1]
    buff += '}'

    configs.update({'configs': json.loads(buff)})
    configs.update({'id': feature_prof.id})

    return configs
