from django.db.models import ProtectedError

from constants import *
from fabric.models import Switch
import linecard
from models import SwitchModel
from utils.exception import IgniteException

import logging
logger = logging.getLogger(__name__)


def get_all_switches(switch_type, tier):
    if switch_type == ALL:
        switches = SwitchModel.objects.all().exclude(pk=1).order_by(NAME)
    else:
        switches = (SwitchModel.objects.filter(switch_type=switch_type).exclude(pk=1).
                    order_by(NAME))

    switch_list = list()

    for switch in switches:
        if tier == ALL or tier in switch.switch_data[TIERS]:
            switch_list.append(switch)

    return switch_list


def add_switch(data, user):
    return _add_switch(data, user)


def _add_switch(data, user, id=0):
    logger.debug("switch name = %s, type = %s", data[NAME],
                 data[SWITCH_TYPE])

    if id:
        # TODO: is there a better way to do this?
        if Switch.objects.filter(model_id=id).count():
            raise IgniteException(ERR_SW_IN_USE)

        # get existing switch
        switch = SwitchModel.objects.get(pk=id)
        # decrement ref count of existing line cards
        if switch.switch_type == FIXED and switch.switch_data[MODULE_ID]:
            linecard.update_ref_count(switch.switch_data[MODULE_ID], -1)
        elif switch.switch_type == CHASSIS:
            for slot in switch.switch_data[SLOTS]:
                linecard.update_ref_count(slot[LC_ID], -1)
    else:
        # create new switch
        switch = SwitchModel()
    switch.name = data[NAME]
    switch.base_model = data[BASE_MODEL]
    switch.switch_type = data[SWITCH_TYPE]
    switch.switch_data = data[SWITCH_DATA]
    switch.updated_by = user
    # generate port & switch info for switch
    switch.switch_info, switch.meta = _generate_switch_info(data[SWITCH_TYPE],
                                                            data[SWITCH_DATA])

    switch.save()

    return switch


def _generate_switch_info(switch_type, data):
    switch_info = dict()
    meta = dict()
    slot_list = []

    for role in PORT_ROLES:
        # for each role, create a list of ports belonging to that role
        switch_info[role] = list()
        meta[role] = list()

    for speed in PORT_SPEEDS:
        # number of ports at each speed
        switch_info[speed] = 0

    if switch_type == FIXED:
        _scan_port_groups(switch_info, meta, 1, data[PORT_GROUPS])

        module_id = data.get(MODULE_ID, 0)

        if module_id:
            module = linecard.get_linecard(module_id)
            linecard.update_ref_count(module_id, 1)
            _scan_port_groups(switch_info, meta, 2, module.lc_data[PORT_GROUPS])
    else:
        for slot in data[SLOTS]:
            lc = linecard.get_linecard(slot[LC_ID])
            linecard.update_ref_count(slot[LC_ID], 1)
            slot_list.append(slot[SLOT_NUM])
            _scan_port_groups(switch_info, meta, slot[SLOT_NUM],
                              lc.lc_data[PORT_GROUPS])

        if len(slot_list) != len(set(slot_list)):
            raise IgniteException(ERR_SW_SLOT_IN_USE)

    return switch_info, meta


def _scan_port_groups(switch_info, meta, slot_num, port_groups):
    port_num = 1

    for port_group in port_groups:
        # form port string in the form of "1/1-48"
        string = (str(slot_num) + "/" + str(port_num) + "-" +
                  str(port_num + port_group[NUM_PORTS] - 1))

        switch_info[port_group[ROLE]].append(string)

        for index in range(0, port_group[NUM_PORTS]):
            # append individual port (like 1/1) to port role list
            port = str(slot_num) + "/" + str(port_num + index)
            meta[port_group[ROLE]].append(port)

        # increment # of ports at this speed
        switch_info[port_group[SPEED]] += port_group[NUM_PORTS]

        # increment port number for next port group
        port_num += port_group[NUM_PORTS]


def get_switch(id):
    return SwitchModel.objects.get(pk=id)


def update_switch(id, data, user):
    return _add_switch(data, user, id)


def delete_switch(id):
    switch = SwitchModel.objects.get(pk=id)

    # decrement ref count of existing line cards
    if switch.switch_type == FIXED and switch.switch_data[MODULE_ID]:
        linecard.update_ref_count(switch.switch_data[MODULE_ID], -1)
    elif switch.switch_type == CHASSIS:
        for slot in switch.switch_data[SLOTS]:
            linecard.update_ref_count(slot[LC_ID], -1)

    try:
        switch.delete()
    except ProtectedError:
        raise IgniteException(ERR_SW_IN_USE)
