from django.db.models import F

from constants import *
from models import LineCard
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_linecards(lc_type):
    if lc_type == ALL:
        linecards = LineCard.objects.all().order_by(NAME)
    else:
        linecards = LineCard.objects.filter(lc_type=lc_type).order_by(NAME)

    return linecards


def add_linecard(data, user):
    return _add_linecard(data, user)


def _add_linecard(data, user, id=0):
    logger.debug("lc name = %s, type = %s", data[NAME], data[LC_TYPE])

    if id:
        # get existing line card
        lc = LineCard.objects.get(pk=id)
        if lc.ref_count:
            raise IgniteException(ERR_LC_IN_USE)
    else:
        # create new line card
        lc = LineCard()

    lc.name = data[NAME]
    lc.lc_type = data[LC_TYPE]
    lc.lc_data = data[LC_DATA]
    lc.updated_by = user
    lc.lc_info = dict()

    for speed in PORT_SPEEDS:
        lc.lc_info[speed] = 0

    for port_group in data[LC_DATA][PORT_GROUPS]:
        lc.lc_info[port_group[SPEED]] += port_group[NUM_PORTS]

    lc.save()

    return lc


def get_linecard(id):
    return LineCard.objects.get(pk=id)


def update_linecard(id, data, user):
    return _add_linecard(data, user, id)


def delete_linecard(id):
    lc = LineCard.objects.get(pk=id)
    if lc.ref_count:
        raise IgniteException(ERR_LC_IN_USE)
    lc.delete()


def update_ref_count(id, value):
    LineCard.objects.filter(pk=id).update(ref_count=F('ref_count')+value)
