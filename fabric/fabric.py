from django.utils import timezone
import json
import requests
import sys
from ignite.settings import BASE_DIR

from netaddr import IPAddress, IPNetwork

from bootstrap.constants import BOOT_SUCCESS
import build
import config.profile as config
from constants import *
from discovery.discoveryrule import find_dup_serial_discovery
from discovery.discoveryrule import find_duplicate
import feature.feature as feature
from group.group import maintenance_group_count
import image.image_profile as image
from models import Fabric, Link, Switch, Topology, SwitchConfig
from switch.switch import get_switch
from topology import BaseTopology
from utils.exception import IgniteException
from workflow.constants import BOOTSTRAP_WORKFLOW_ID
import workflow.workflow as workflow
from utils.utils import ports_to_string
from bootstrap.constants import BOOT_PROGRESS, BOOT_FAIL
from pool.pool import _validate_pool
from pool.constants import IPV4
from group.scripts.upgrade import get_nxapi_template, build_nxapi_url
import logging
logger = logging.getLogger(__name__)


def get_all_fabrics():
    return Fabric.objects.filter(is_saved=True).order_by(NAME)


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
    top.maintenance_group_count = maintenance_group_count(fab_id)
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
    if switch.boot_detail:
        if data[CONFIG_TYPE] == RUNNING_CONFIG:
            logger.debug("input config type- " + data[CONFIG_TYPE])
            if SwitchConfig.objects.filter(switch_id=switch_id):
                switch.config_type = data[CONFIG_TYPE]
            else:
                logger.error(ERR_RUN_CONFIG_NOT_AVAL)
                raise IgniteException(ERR_RUN_CONFIG_NOT_AVAL)
        else:
            switch.config_type = data[CONFIG_TYPE]

        if any([switch.name != data[NAME], switch.model.id != data[MODEL], switch.serial_num != data[SERIAL_NUM]]):
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

    if change:
        if data[MODEL] == 1:
            logger.debug("Unknown switch model can not be assigned")
            raise IgniteException(ERR_CAN_NOT_ASSIGN_UNKOWN_MODEL)

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


def decommission_switch(fab_id, switch_id, user):
    BaseTopology.get_object(fab_id, user).decommission_switch(switch_id)


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


def clone_fabric(fab_id, data, user=""):

    old_fabric = Topology.objects.get(pk=fab_id)

    # create new fabric
    new_fabric = Fabric()
    new_fabric.name = data[NAME]
    new_fabric.model_name = old_fabric.model_name
    new_fabric.is_fabric = True

    if old_fabric.config_profile:
        new_fabric.config_profile = old_fabric.config_profile
    if old_fabric.feature_profile:
        new_fabric.feature_profile = old_fabric.feature_profile

    new_fabric.updated_by = user
    new_fabric.save()

    # fabric defaults, switches & links objects
    new_fabric.defaults = dict()
    new_fabric.defaults[SWITCHES] = list()
    new_fabric.defaults[LINKS] = list()
    new_fabric.switches = list()
    new_fabric.links = list()

    switch_dict = dict()

    for switch in Switch.objects.filter(topology_id=old_fabric.id
                                        ).order_by(ID):
        # save id for later
        switch_id = switch.id

        switch.id = None
        switch.topology = new_fabric
        switch.serial_num = ""
        switch.boot_detail = None

        if not switch.dummy:
            # append fabric name to switch name
            if data[NAME_OPERATION] == REPLACE:
                name = switch.name.replace(old_fabric.name, new_fabric.name)
                if Switch.objects.filter(name=name):
                    raise IgniteException(ERR_CLONE_FABRIC)
                switch.name = name
            elif data[NAME_OPERATION] == PREPEND:
                name = new_fabric.name + "_" + switch.name
                if Switch.objects.filter(name=name):
                    raise IgniteException(ERR_CLONE_FABRIC)
                switch.name = name

        switch.save()

        # store fabric switch id to switch mapping
        switch_dict[switch_id] = switch

        if switch.dummy:
            new_fabric.defaults[SWITCHES].append(switch)
        else:
            new_fabric.switches.append(switch)

    for link in Link.objects.filter(topology_id=old_fabric.id):
        link.id = None
        link.topology = new_fabric

        if link.src_switch:
            link.src_switch = switch_dict[link.src_switch.id]
            link.dst_switch = switch_dict[link.dst_switch.id]
        else:
            link.src_switch = None
            link.dst_switch = None

        link.save()

        if not link.dummy:
            new_fabric.links.append(link)
        elif link.dummy and not link.src_switch:
            link.src_tier = link.src_ports
            link.dst_tier = link.dst_ports
            new_fabric.defaults[LINKS].append(link)
    new_fabric.save()

    return new_fabric


def create_empty_fabric(data):

    logger.debug("creating empty fabric")
    fabric = Fabric()
    fabric.model_name = LEAF_SPINE
    fabric.is_fabric = True
    fabric.is_saved = False
    fabric.is_discovered = True
    fabric.save()

    fabric.defaults = dict()
    fabric.defaults[SWITCHES] = list()
    fabric.defaults[LINKS] = list()

    # add switch to discovery defaults
    logger.debug("Assigning defaults to dummy fabric")
    fabric.defaults[SWITCHES].append(get_default_discovery_switch(fabric.id, SPINE))
    fabric.defaults[SWITCHES].append(get_default_discovery_switch(fabric.id, LEAF))
    fabric.defaults[LINKS].append(get_default_discovery_link(fabric.id))
    logger.debug("Fabric created")
    return fabric.id


def get_default_discovery_switch(fab_id, tier):
    logger.debug("creating default switch")

    switch_default = Switch()
    switch_default.topology_id = fab_id
    switch_default.dummy = True
    switch_default.name = DEFAULT
    switch_default.tier = tier
    switch_default.model = get_switch(1)
    switch_default.image_profile = image.get_profile(1)
    switch_default.save()
    logger.debug("default switch created")
    return switch_default


def get_default_discovery_link(fab_id):
    logger.debug("creating default link for discovery")

    link_default = Link()
    link_default.topology_id = fab_id
    link_default.dummy = True
    link_default.src_ports = SPINE
    link_default.dst_ports = LEAF
    link_default.link_type = PHYSICAL
    link_default.num_links = 1
    link_default.save()
    logger.debug("Default link created")
    return link_default


def save_discovered_fabric(fab_id, data, user):
    logger.debug("Start saving discovered Fabric")

    fabric = Fabric.objects.get(pk=fab_id)
    fabric.name = data[NAME]
    fabric.config_profile = config.get_profile(1)
    fabric.updated_by = user
    fabric.submit = True
    fabric.save()

    logger.debug("fabric name = %s", data[NAME])

    cfg = dict()
    feat = dict()
    wf = dict()
    switch_dict = dict()

    for switch in Switch.objects.filter(topology_id=fab_id).order_by(ID):

        logger.debug("Looping through all switches of Discovered fabric- %s", data[NAME])

        if switch.dummy:
            # set default config profile for fabric default switch
            logger.debug("set default config profile for fabric default switch")
            switch.config_profile = config.get_profile(1)
        else:
            # append fabric name to switch name
            logger.debug("Defining switch name by appending it to fabric name for switch-%s", switch.name)
            switch.name = fabric.name + "_" + switch.name

        # set Unknown model to switch in fabric
        logger.debug("set Unknown model to switch in fabric")
        switch.model = get_switch(1)
        logger.debug("Added Unknown model to switch in fabric")
        switch.save()
    fabric.is_saved = True
    fabric.save()

    logger.debug("Fabric saved")

    return fabric


def get_discovery(fab_id, data):
    # to discover switches and create fabric

    logger.debug("Start Discovering the fabric")

    if data[SPINE_IP] == data[LEAF_IP]:
        # check if spine and leaf given by user are same
        logger.debug(ERR_SAME_SPINE_LEAF_IP)
        raise IgniteException(ERR_SAME_SPINE_LEAF_IP)
    connectivities = dict()
    logger.debug("Getting cdp information for spine with IP-%s", data[SPINE_IP])
    # getting information for spine
    spine_name, connectivities[SPINE], spine_serial_num = get_cdp_info(data, str(data[SPINE_IP]))

    # check whether information for spine received or not
    if not spine_name and not connectivities[SPINE]:
        logger.debug(ERR_UNABLE_TO_GET_SPINE_SWITCH_INFO)
        raise IgniteException(ERR_UNABLE_TO_GET_SPINE_SWITCH_INFO)
    logger.debug("Successfully got information for spine with spine IP-%s", data[SPINE_IP])
    logger.debug("Spine: Switch name:%s, Serial number=%s", spine_name, spine_serial_num)

    logger.debug("Getting cdp information for Leaf with IP-%s", data[LEAF_IP])
    # getting information for leaf
    leaf_name, connectivities[LEAF], leaf_serial_num = get_cdp_info(data, data[LEAF_IP])

    # check whether information for leaf received or not
    if not leaf_name and not connectivities[LEAF]:
        logger.debug(ERR_UNABLE_TO_GET_LEAF_SWITCH_INFO)
        raise IgniteException(ERR_UNABLE_TO_GET_LEAF_SWITCH_INFO)
    logger.debug("Successfully got information for leaf with spine IP-%s", data[LEAF_IP])
    logger.debug("LEAF: Switch name:%s, Serial number=%s", leaf_name, leaf_serial_num)

    # get neighbors of spine and leaf from connectivities
    neigh_dict = get_neighbors(connectivities)
    logger.debug("Validating IP range")
    _validate_pool(data[IP_RANGE], IPV4)
    logger.debug("IP range validated")
    tiers, all_connectivites, ip_neigh, switch_with_ip = get_ip_range_info(data, neigh_dict)
    if [spine_name, spine_serial_num] not in tiers[SPINE]:
        tiers[SPINE].append([spine_name, spine_serial_num])
        all_connectivites.append(connectivities[SPINE])

    logger.debug("LEAF TIERS :%s", tiers)
    if [leaf_name, leaf_serial_num] not in tiers[LEAF]:
        logger.debug("LEAF IS NOT IN RANGE")
        tiers[LEAF].append([leaf_name, leaf_serial_num])
        all_connectivites.append(connectivities[LEAF])

    tiers = update_borders_and_cores(tiers, ip_neigh)

    switch_id_details = add_discovered_switches(fab_id, tiers, switch_with_ip)
    add_discovered_links(fab_id, switch_id_details, all_connectivites, tiers)
    logger.debug("Discovery is completed")


def get_cdp_info(data, ip):
    import types
    try:
        url = build_nxapi_url(ip)
        logger.debug("URL is %s", url)
        myheaders = {'content-type': 'application/json-rpc'}
        commands = []
        commands.append('show inv')
        commands.append('show switchname')
        commands.append('show cdp neighbor')
        template = get_nxapi_template()
        template["method"] = "cli"
        for c in range(0, len(commands)):
            payload = []
            template['params']['cmd'] = commands[c]
            payload.append(template)
            logger.debug("Username:%s, Password:%s", data['auth_details']['username'], data['auth_details']['password'])
            response = requests.post(url, data=json.dumps(payload),
                                     headers=myheaders,
                                     auth=(str(data['auth_details']['username']),
                                     str(data['auth_details']['password']))).json()
            if c == 0:
                serial_number = response['result']['body']['TABLE_inv'][u'ROW_inv'][0]['serialnum']
            elif c == 1:
                switchname = response["result"]["body"]["hostname"]
            else:
                neighbors = response["result"]["body"]["TABLE_cdp_neighbor_brief_info"]["ROW_cdp_neighbor_brief_info"]

        connectivity_list = list()
        for i in range(0, len(neighbors)):
            remote_switch = neighbors[i]["device_id"]
            index = remote_switch.find("(")
            if index != -1:
                remote_switch = remote_switch[0:index]
            if not neighbors[i]["intf_id"].startswith('mgmt'):
                one_neighbor = '{0};{1};{2};{3}'.format(switchname,
                                                        neighbors[i]["intf_id"],
                                                        remote_switch,
                                                        neighbors[i]["port_id"])

                connectivity_list.append(one_neighbor)
        return switchname, connectivity_list, serial_number
    except:
        return None, None, None


def get_neighbors(connectivities):
    logger.debug("Identifying neighbors using connectivity information")
    neighbor = dict()
    neighbor[SPINE] = list()
    neighbor[LEAF] = list()
    for link in connectivities[SPINE]:
        neighbor[SPINE].append(link.split(';')[2])
    for link in connectivities[LEAF]:
        neighbor[LEAF].append(link.split(';')[2])
    logger.debug("Neighbors Identified")
    return neighbor


# identifying Spine(s) and Leaf(s) from ip range
def get_ip_range_info(data, neigh_dict):
    logger.debug("Identifyinh tier roles(Spine/Leaf) in Ip range")
    tiers = dict()
    tiers[SPINE] = list()
    tiers[LEAF] = list()
    tiers[CORE] = list()
    tiers[BORDER] = list()
    ip_neigh = dict()
    ip_neigh[SPINE] = dict()
    ip_neigh[LEAF] = dict()
    all_connectivites = list()
    switch_with_ip = {}
    for range_ip in data[IP_RANGE]:
        logger.debug("For range:%s", range_ip)
        start = IPNetwork(range_ip[START])
        end = IPNetwork(range_ip[END])
        for ip in range(start.ip, end.ip + 1):
            logger.debug("Getting Info for IP = %s", str(IPAddress(ip)))
            neighbor = list()
            switch_name, ip_connections, serial_number = get_cdp_info(data, str(IPAddress(ip)))
            if not switch_name and not ip_connections:
                logger.debug("Switch info not found for IP-%s", str(IPAddress(ip)))
                continue
            if ip_connections and switch_name:
                logger.debug("Found info for IP-%s in ip_range", str(IPAddress(ip)))
                logger.debug("switch name:%s, serial_number:%s", switch_name, serial_number)
                all_connectivites.append(ip_connections)
                switch_with_ip[switch_name] = str(IPAddress(ip)) + "/" + str(start.prefixlen)
                for link in ip_connections:
                    logger.debug("Taking its neighbor:%s", link.split(';')[2])
                    neighbor.append(link.split(';')[2])
                logger.debug("Neighbor set is %s", set(neighbor))
                logger.debug("neigh_dict[SPINE] is %s", set(neigh_dict[SPINE]))
                if set(neighbor) & set(neigh_dict[SPINE]):
                    # it is spine
                    logger.debug("Switch is found as spine")
                    ip_neigh[SPINE][switch_name] = neighbor
                    tiers[SPINE].append([switch_name, serial_number])
                    logger.debug("Spines are:%s", tiers[SPINE])
                elif switch_name in set(neigh_dict[SPINE]):
                    # it is leaf
                    logger.debug("Switch is found as leaf")
                    ip_neigh[LEAF][switch_name] = neighbor
                    tiers[LEAF].append([switch_name, serial_number])

    logger.debug("Found tiers and connections for all switches in ip_range")
    return tiers, all_connectivites, ip_neigh, switch_with_ip


def update_borders_and_cores(tiers, ip_neigh):
    list_spine = [sub[0] for sub in tiers[SPINE]]
    logger.debug("Spines are %s", list_spine)

    list_leaf = [sub[0] for sub in tiers[LEAF]]
    logger.debug("Leafs are :%s", list_leaf)
    for key, value in ip_neigh[SPINE].iteritems():
        if (set(value)-set(list_leaf)):
            logger.debug("Found Cores")
            tiers[CORE].append(list(set(value)-set(list_leaf)))
            logger.debug("Core Found is :%s", tiers[CORE])
    tiers[CORE] = list(set([item for sublist in tiers[CORE] for item in sublist]))
    logger.debug("Cores are :%s", tiers[CORE])
    for key, value in ip_neigh[LEAF].iteritems():
        if (set(value)-set(list_spine)):
            logger.debug("Found Border")
            tiers[BORDER].append(list(set(value)-set(list_spine)))
    tiers[BORDER] = list(set([item for sublist in tiers[BORDER] for item in sublist]))
    logger.debug("Borders are :%s", tiers[BORDER])
    return tiers

def add_discovered_switches(fab_id, tiers, switch_with_ip):
    from bootstrap import bootstrap
    logger.debug("Adding discovered switches in fabric")
    switch_id_details = dict()
    switch_id_details[SPINE] = dict()
    switch_id_details[LEAF] = dict()
    switch_id_details[CORE] = dict()
    switch_id_details[BORDER] = dict()
    for spine_switch in tiers[SPINE]:
        logger.debug("Adding spine switch:%s in fabric", spine_switch[0])
        switch = Switch()
        switch.tier = SPINE
        switch.name = spine_switch[0]
        switch.dummy = False
        switch.serial_num = spine_switch[1]
        find_duplicate([spine_switch[1]])
        switch.topology_id = fab_id
        switch.mgmt_ip = switch_with_ip[spine_switch[0]]
        switch.save()
        bootstrap.update_boot_detail(switch,
                                      match_type=DISCOVERY,
                                      discovery_rule=None,
                                      boot_time=timezone.now(),
                                      boot_status=BOOT_SUCCESS,
                                      model_type='')
        logger.debug("Spine added")
        switch_id_details[SPINE][spine_switch[0]] = switch.id
    for leaf_switch in tiers[LEAF]:
        logger.debug("Adding leaf switch:%s to fabric", leaf_switch[0])
        switch = Switch()
        switch.tier = LEAF
        switch.name = leaf_switch[0]
        switch.serial_num = leaf_switch[1]
        find_duplicate([leaf_switch[1]])
        switch.topology_id = fab_id
        switch.mgmt_ip = switch_with_ip[leaf_switch[0]]
        switch.save()
        bootstrap.update_boot_detail(switch,
                                      match_type=DISCOVERY,
                                      discovery_rule=None,
                                      boot_time=timezone.now(),
                                      boot_status=BOOT_SUCCESS,
                                      model_type='')
        logger.debug("Leaf added")
        switch_id_details[LEAF][leaf_switch[0]] = switch.id
    for core_switch in tiers[CORE]:
        logger.debug("Adding core switch:%s in fabric", core_switch)
        switch = Switch()
        switch.tier = CORE
        switch.name = core_switch
        switch.dummy = False
        switch.topology_id = fab_id
        switch.save()
        bootstrap.update_boot_detail(switch,
                                      match_type=DISCOVERY,
                                      discovery_rule=None,
                                      boot_time=timezone.now(),
                                      boot_status=BOOT_SUCCESS,
                                      model_type='')
        logger.debug("core added")
        switch_id_details[CORE][core_switch] = switch.id
    for border_switch in tiers[BORDER]:
        logger.debug("Adding border switch:%s in fabric", border_switch)
        switch = Switch()
        switch.tier = BORDER
        switch.name = border_switch
        switch.dummy = False
        switch.topology_id = fab_id
        switch.save()
        bootstrap.update_boot_detail(switch,
                                      match_type=DISCOVERY,
                                      discovery_rule=None,
                                      boot_time=timezone.now(),
                                      boot_status=BOOT_SUCCESS,
                                      model_type='')
        logger.debug("Border added")
        switch_id_details[BORDER][border_switch] = switch.id

    return switch_id_details


def add_discovered_links(fab_id, switch_id_details, connectivities, tiers):
    logger.debug("Adding discovered links between switches in discovered fabric")
    ports_info = get_ports_info(connectivities, tiers[BORDER], tiers[CORE])
    used_switch = list()
    for i in range(0, len(connectivities)):
        for j in range(0, len(connectivities[i])):
            ssw = connectivities[i][j].split(';')[0]
            dsw = connectivities[i][j].split(';')[2]
            if (ssw != dsw):
                if (ssw in switch_id_details[SPINE].keys() and \
                    dsw in switch_id_details[LEAF].keys()):

                    logger.debug("Source switch %s is Spine and Destination switch %s is Leaf", ssw, dsw)
                    link_type = PHYSICAL
                    src_switch = switch_id_details[SPINE][ssw]
                    dst_switch = switch_id_details[LEAF][dsw]
                elif (ssw in switch_id_details[LEAF].keys() and \
                         dsw in switch_id_details[LEAF].keys()):
                    logger.debug("Source switch %s is Leaf and Destination switch %s is Leaf", ssw, dsw)
                    link_type = VPC_PEER
                    src_switch = switch_id_details[LEAF][ssw]
                    dst_switch = switch_id_details[LEAF][dsw]
                elif (ssw in switch_id_details[SPINE].keys() and \
                      dsw in switch_id_details[CORE].keys()):
                    logger.debug("Source switch %s is Spine and Destination switch %s is CORE", ssw, dsw)
                    link_type = PHYSICAL
                    src_switch = switch_id_details[SPINE][ssw]
                    dst_switch = switch_id_details[CORE][dsw]
                elif (ssw in switch_id_details[LEAF].keys() and \
                           dsw in switch_id_details[BORDER].keys()):
                    logger.debug("Source switch %s is LEAF and Destination switch %s is Border", ssw, dsw)
                    link_type = PHYSICAL
                    src_switch = switch_id_details[LEAF][ssw]
                    dst_switch = switch_id_details[BORDER][dsw]
                else:
                    logger.debug("No ssw/dsw found")
                    continue

                temp_list = list()
                temp_list.append(src_switch)
                temp_list.append(dst_switch)
                if temp_list not in used_switch:
                    used_switch.append(temp_list)
                    for switches in ports_info:
                        for neigh in ports_info[switches]:
                            if switches == ssw and neigh == dsw:
                                logger.debug("Finding source ports and destination ports for link between switches %s and %s", ssw, dsw)
                                src_ports_list = ports_info[switches][neigh][0]
                                dst_ports_list = ports_info[switches][neigh][1]
                                logger.debug("Ports are %s and %s", src_ports_list, dst_ports_list)
                    link = Link()
                    link.topology_id = fab_id
                    link.dummy = False
                    link.link_type = link_type
                    link.num_links = 1
                    link.src_switch_id = src_switch
                    link.dst_switch_id = dst_switch
                    link.src_ports = ports_to_string(src_ports_list)
                    link.dst_ports = ports_to_string(dst_ports_list)
                    link.save()
                    logger.debug("Link created")


def get_ports_info(connectivities, borders, cores):
    logger.debug("getting port information")
    switches = [connection[0].split(';')[0] for connection in connectivities]
    if borders:
        for border in borders:
            switches.append(border)
    if cores:
        for core in cores:
            switches.append(core)

    ports_info = dict()
    for i in range(len(switches)):
        ssw = switches[i]
        ports_info[ssw] = dict()
        for j in range(len(switches)):
            dsw = switches[j]
            ports_info[ssw][dsw] = list()
            temp_src_list = list()
            temp_dst_list = list()
            for conn in connectivities:
                for c in conn:
                    if c.split(';')[0] == ssw and c.split(';')[2] == dsw:
                        temp_src_list.append(c.split(';')[1])
                        temp_dst_list.append(c.split(';')[3])
                ports_info[ssw][dsw].append(temp_src_list)
                ports_info[ssw][dsw].append(temp_dst_list)
    return ports_info


def delete_discovered_fabric(fab_id):
    try:
        for switch in Switch.objects.filter(topology_id=fab_id):
            # delete switch and boot detail if any
            boot_detail = switch.boot_detail
            try:
                switch.delete()
            except Exception as e:
                pass

            if boot_detail:
                boot_detail.delete()
        Topology.objects.get(id=fab_id).delete()
    except Exception as e:
        logger.error(e)


# reset boot details of switch in fabric
def reset_switch_boot_status(sw_id):
    switch = Switch.objects.get(id=sw_id)
    if switch:
        logger.debug("Switch found")
        if switch.boot_detail:
            logger.debug("Switch has boot state as %s ", switch.boot_detail.boot_status)
            if switch.boot_detail.boot_status in [BOOT_PROGRESS, BOOT_FAIL]:
                boot_detail = switch.boot_detail
                if switch.boot_detail.boot_status == BOOT_PROGRESS:
                    logger.debug("Updating boot_in_progress in switch Model")
                    switch.model.boot_in_progress -= 1
                else:
                    logger.debug("Updating boot_with_fail in switch Model")
                    switch.model.booted_with_fail -= 1
                switch.model.save()

                switch.boot_detail = None
                switch.save()
                logger.debug("Switch updated")
                logger.debug("Deleting boot details for switch")
                boot_detail.delete()
                logger.debug("Boot details deleted")
                fabric = get_fabric(switch.topology_id)
                return fabric
            logger.debug("Can not reset the switch as it is in Boot state:  %s ", switch.boot_detail.boot_status)
            raise IgniteException(ERR_CAN_NOT_RESET + switch.boot_detail.boot_status)
        raise IgniteException(ERR_SWITCH_NOT_BOOTED)
