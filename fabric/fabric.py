import build
import config.profile as config
from constants import *
from discovery.discoveryrule import find_dup_serial_discovery
import feature.feature as feature
import image.image_profile as image
from models import Fabric, Link, Switch, Topology
from switch.switch import get_switch
from topology import BaseTopology
from utils.exception import IgniteException
from workflow.constants import BOOTSTRAP_WORKFLOW_ID
import workflow.workflow as workflow

import logging
logger = logging.getLogger(__name__)


def get_all_fabrics():
    return Fabric.objects.all().order_by(NAME)


def add_fabric(data, user):
    # get topology
    top = Topology.objects.get(pk=data[TOPOLOGY])

    logger.debug("fabric name = %s, topology name = %s, model = %s",
                 data[NAME], top.name, top.model_name)

    # create new fabric
    fabric = Fabric()
    fabric.name = data[NAME]
    fabric.model_name = top.model_name
    fabric.is_fabric = True

    if data[CONFIG_PROFILE]:
        fabric.config_profile = config.get_profile(data[CONFIG_PROFILE])
    if data[FEATURE_PROFILE]:
        fabric.feature_profile = feature.get_profile(data[FEATURE_PROFILE])
    fabric.updated_by = user
    fabric.save()

    cfg = dict()
    feat = dict()
    wf = dict()

    # store tier default config & feature profile
    for item in data[SWITCHES]:
        # if profile id is zero, then store null
        # it means - do not apply config/feature/workflow for this tier
        if item[CONFIG_PROFILE]:
            cfg[item[TIER]] = config.get_profile(item[CONFIG_PROFILE])
        else:
            cfg[item[TIER]] = None

        if item[FEATURE_PROFILE]:
            feat[item[TIER]] = feature.get_profile(item[FEATURE_PROFILE])
        else:
            feat[item[TIER]] = None

        if item[WORKFLOW]:
            wf[item[TIER]] = workflow.get_workflow(item[WORKFLOW])
        else:
            wf[item[TIER]] = None

    # fabric defaults, switches & links objects
    fabric.defaults = dict()
    fabric.defaults[SWITCHES] = list()
    fabric.defaults[LINKS] = list()
    fabric.switches = list()
    fabric.links = list()

    # map of topology switch id to fabric switch object
    # needed when creating fabric links
    switch_dict = dict()

    # duplicate all topology switches into fabric
    for switch in Switch.objects.filter(topology_id=top.id).order_by(ID):
        # save id for later
        switch_id = switch.id

        switch.id = None
        switch.topology = fabric

        if switch.dummy:
            # set config & feature profile for fabric default switch
            switch.config_profile = cfg[switch.tier]
            switch.feature_profile = feat[switch.tier]
            switch.workflow = wf[switch.tier]
        else:
            # append fabric name to switch name
            switch.name = fabric.name + "_" + switch.name

        switch.save()

        # store topology switch id to switch mapping
        switch_dict[switch_id] = switch

        if switch.dummy:
            fabric.defaults[SWITCHES].append(switch)
        else:
            fabric.switches.append(switch)

    # duplicate all topology links into fabric
    for link in Link.objects.filter(topology_id=top.id):
        link.id = None
        link.topology = fabric

        if link.src_switch:
            link.src_switch = switch_dict[link.src_switch.id]
            link.dst_switch = switch_dict[link.dst_switch.id]
        else:
            link.src_switch = None
            link.dst_switch = None

        link.save()

        if not link.dummy:
            fabric.links.append(link)
        elif link.dummy and not link.src_switch:
            link.src_tier = link.src_ports
            link.dst_tier = link.dst_ports
            fabric.defaults[LINKS].append(link)

    return fabric


def get_fabric(fab_id):
    # get topology info, then add fabric info
    top = BaseTopology.get_topology(fab_id)
    top.site = top.fabric.site
    return top


def update_fabric_name(fab_id, data, user):
    logger.debug("fabric id = %d, name = %s", fab_id, data[NAME])

    if (Switch.objects.filter(topology_id=fab_id,
                              boot_detail__boot_status__isnull=False).count()):
        raise IgniteException(ERR_NO_NAME_CHANGE)

    fabric = Fabric.objects.get(pk=fab_id)

    if (fabric.name == data[NAME]):
        return

    old_name = fabric.name
    fabric.name = data[NAME]
    fabric.updated_by = user
    fabric.save()

    switches = Switch.objects.filter(topology_id=fab_id, dummy=False)

    for switch in switches:
        switch.name = switch.name.replace(old_name, fabric.name)
        switch.save()


def delete_fabric(fab_id):
    BaseTopology.delete_topology(fab_id)


def add_switches(fab_id, data, user):
    BaseTopology.get_object(fab_id, user).add_switches(data)


def update_switch(fab_id, switch_id, data, user):
    switch = Switch.objects.get(pk=switch_id)

    # check if switch is already booted
    if switch.boot_detail and switch.boot_detail.boot_status:
        raise IgniteException(ERR_NO_NAME_CHANGE)

    # check if switch already exists with new name
    # switch name is searched across all fabrics
    if (switch.name != data[NAME] and
            Switch.objects.filter(topology__is_fabric=True, dummy=False,
                                  name=data[NAME])):
        raise IgniteException(ERR_SW_NAME_IN_USE)

    switch.name = data[NAME]

    # check if switch already exists with new serial num
    # note: serial numbers are unique across fabrics
    if (data[SERIAL_NUM] and switch.serial_num != data[SERIAL_NUM] and
            Switch.objects.filter(dummy=False, serial_num=data[SERIAL_NUM])):
        raise IgniteException(ERR_SERIAL_NUM_IN_USE)
    # check if serial_num exists in discovery rules
    find_dup_serial_discovery([data[SERIAL_NUM]])
    switch.serial_num = data[SERIAL_NUM]

    new_model = get_switch(data[MODEL])

    # is there a change in model?
    change = True if new_model != switch.model else False
    logger.debug("%schange in switch model", "no " if not change else "")

    # save new values
    switch.model = new_model
    switch.image_profile = (image.get_profile(data[IMAGE_PROFILE])
                            if data[IMAGE_PROFILE] else None)
    switch.config_profile = (config.get_profile(data[CONFIG_PROFILE])
                             if data[CONFIG_PROFILE] else None)
    switch.feature_profile = (feature.get_profile(data[FEATURE_PROFILE])
                              if data[FEATURE_PROFILE] else None)
    switch.workflow = (workflow.get_workflow(data[WORKFLOW])
                       if data[WORKFLOW] else None)

    switch.save()

    if change:
        BaseTopology.get_object(fab_id, user).update_model(switch)
    else:
        Fabric.objects.filter(pk=fab_id).update(updated_by=user)


def delete_switch(fab_id, switch_id, user):
    BaseTopology.get_object(fab_id, user).delete_switch(switch_id)


def add_link(fab_id, data, user):
    BaseTopology.get_object(fab_id, user).add_link(data)


def update_link(fab_id, link_id, data, user):
    BaseTopology.get_object(fab_id, user).update_link(link_id, data)


def delete_link(fab_id, link_id, user):
    BaseTopology.get_object(fab_id, user).delete_link(link_id, True)


def set_submit(fab_id, data, user):
    BaseTopology.set_submit(fab_id, data, user)


def update_defaults(fab_id, data, user):
    BaseTopology.get_object(fab_id, user).update_defaults(data)


def update_profiles(fab_id, data, user):
    # setting global level config and feture profiles
    fabric = Fabric.objects.get(pk=fab_id)

    if data[CONFIG_PROFILE]:
        fabric.config_profile = config.get_profile(data[CONFIG_PROFILE])
    else:
        fabric.config_profile = None

    if data[FEATURE_PROFILE]:
        fabric.feature_profile = feature.get_profile(data[FEATURE_PROFILE])
    else:
        fabric.feature_profile = None
    fabric.save()

    cfg = dict()
    feat = dict()
    wf = dict()

    # store tier default config & feature profile
    for item in data[PROFILES]:
        # if profile id is zero, then store null
        # it means - do not apply config/feature/workflow for this tier
        if item[CONFIG_PROFILE]:
            cfg[item[TIER]] = config.get_profile(item[CONFIG_PROFILE])
        else:
            cfg[item[TIER]] = None

        if item[FEATURE_PROFILE]:
            feat[item[TIER]] = feature.get_profile(item[FEATURE_PROFILE])
        else:
            feat[item[TIER]] = None

        if item[WORKFLOW]:
            wf[item[TIER]] = workflow.get_workflow(item[WORKFLOW])
        else:
            wf[item[TIER]] = None

    # update profiles in fabric default switches
    for switch in Switch.objects.filter(topology_id=fab_id, dummy=True):
        switch.config_profile = cfg[switch.tier]
        switch.feature_profile = feat[switch.tier]
        switch.workflow = wf[switch.tier]
        switch.save()

    Fabric.objects.filter(pk=fab_id).update(updated_by=user)


def get_all_switches(fab_id, build=True):
    return BaseTopology.get_object(fab_id).get_all_switches(build)


def get_switch_config_profile(switch):
    # if switch specific value set, then return
    if switch.config_profile:
        return switch.config_profile

    # else fetch tier default value
    default = Switch.objects.get(topology_id=switch.topology_id,
                                 tier=switch.tier, dummy=True)
    return default.config_profile


def get_switch_feature_profile(switch):
    # if switch specific value set, then return
    if switch.feature_profile:
        return switch.feature_profile

    # else fetch tier default value
    default = Switch.objects.get(topology_id=switch.topology_id,
                                 tier=switch.tier, dummy=True)
    return default.feature_profile


def get_switch_workflow(switch):
    # if switch specific value set, then return
    if switch.workflow:
        return switch.workflow

    # else fetch tier default value
    default = Switch.objects.get(topology_id=switch.topology_id,
                                 tier=switch.tier, dummy=True)

    if default.workflow:
        return default.workflow

    return workflow.get_workflow(BOOTSTRAP_WORKFLOW_ID)


def get_switch_image(switch):
    # if switch specific value set, then return
    if switch.image_profile:
        return switch.image_profile

    # else fetch tier default value
    default = Switch.objects.get(topology_id=switch.topology_id,
                                 tier=switch.tier, dummy=True)
    return default.image_profile


def get_topology_detail(fab_id):
    return BaseTopology.get_topology_detail(fab_id)


def search_fabric(request):
    serial_number = request[SERIAL_NUM]
    neighbor_data = request[NEIGHBOR_LIST]
    local_node = None
    logger.debug("Received CDP request for switch serial ID %s" % serial_number)

    for neigh in neighbor_data:
        remote_node = neigh[REMOTE_NODE]
        remote_port = neigh[REMOTE_PORT].replace('Ethernet', '')
        local_port = neigh[LOCAL_PORT].replace('Ethernet', '')
        logger.debug("Neighbour info \
                     Remote node %s Remote port %s Local port %s"
                     % (remote_node, remote_port, local_port))

        try:
            link = Link.objects.get(src_switch__name=remote_node,
                                    src_ports=remote_port,
                                    dst_ports=local_port,
                                    link_type=PHYSICAL,
                                    num_links=1,
                                    topology__is_fabric=True)
            logger.debug("Match found for switch %s" % link.dst_switch.name)
            return link.dst_switch, NEIGHBOR
        except Link.DoesNotExist:
            pass

        try:
            link = Link.objects.get(dst_switch__name=remote_node,
                                    dst_ports=remote_port,
                                    src_ports=local_port,
                                    link_type=PHYSICAL,
                                    num_links=1,
                                    topology__is_fabric=True)
            logger.debug("Match found for switch %s" % link.src_switch.name)
            return link.src_switch, NEIGHBOR
        except Link.DoesNotExist:
            pass

    try:
        return Switch.objects.get(serial_num=serial_number,
                                  topology__isnull=False), SERIAL_NUMBER
    except Switch.DoesNotExist:
        return None, None
