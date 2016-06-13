from django.db import transaction

import build
from constants import MODEL_NAME
import fabric
import topology
from serializers import *
import switch_config
from topology import BaseTopology
from utils.exception import IgniteException


def get_all_topologies(submit):
    top_list = BaseTopology.get_all_topologies(submit)
    serializer = TopologyBriefSerializer(top_list, many=True)
    return serializer.data


@transaction.atomic
def add_topology(data, user=""):
    serializer = TopologyPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    top = BaseTopology.create_object(serializer.data[MODEL_NAME])
    serializer = TopologySerializer(top.add_topology(serializer.data, user))
    return serializer.data


def get_topology(top_id):
    top = BaseTopology.get_topology(top_id)
    serializer = TopologySerializer(top)
    return serializer.data


@transaction.atomic
def update_topology_name(top_id, data, user=""):
    serializer = NameSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    BaseTopology.update_topology_name(top_id, serializer.data, user)


@transaction.atomic
def delete_topology(top_id):
    BaseTopology.delete_topology(top_id)


@transaction.atomic
def add_topology_switch(top_id, data, user=""):
    serializer = SwitchPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    BaseTopology.get_object(top_id, user).add_switches(serializer.data)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def update_topology_switch(top_id, switch_id, data, user=""):
    serializer = TopologySwitchPutSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    BaseTopology.get_object(top_id, user).update_switch(switch_id,
                                                        serializer.data)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def delete_topology_switch(top_id, switch_id, user=""):
    BaseTopology.get_object(top_id, user).delete_switch(switch_id)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def add_topology_link(top_id, data, user=""):
    serializer = LinkPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    BaseTopology.get_object(top_id, user).add_link(serializer.data)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def delete_topology_link(top_id, link_id, user=""):
    BaseTopology.get_object(top_id, user).delete_link(link_id)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@ transaction.atomic
def set_topology_submit(top_id, user):
    BaseTopology.set_submit(top_id, True, user)


@transaction.atomic
def clear_topology(top_id, user=""):
    BaseTopology.clear_topology(top_id, user)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def update_topology_defaults(top_id, data, user=""):
    serializer = TopologyPostDefaultsSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    BaseTopology.get_object(top_id, user).update_defaults(serializer.data)
    serializer = TopologySerializer(BaseTopology.get_topology(top_id))
    return serializer.data


@transaction.atomic
def clone_topology(top_id, data, user=""):
    serializer = CloneTopoSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    new_top = topology.clone_topology(top_id, data, user)
    serializer = TopologySerializer(new_top)
    return serializer.data


def get_all_fabrics():
    fabric_list = fabric.get_all_fabrics()
    serializer = FabricBriefSerializer(fabric_list, many=True)
    return serializer.data


@transaction.atomic
def add_fabric(data, user):
    serializer = FabricPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fab = fabric.add_fabric(data, user)
    serializer = FabricSerializer(fab)
    return serializer.data


def get_fabric(fab_id):
    fab = fabric.get_fabric(fab_id)
    serializer = FabricSerializer(fab)
    return serializer.data


@transaction.atomic
def update_fabric_name(fab_id, data, user=""):
    serializer = NameSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fabric.update_fabric_name(fab_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def delete_fabric(fab_id):
    fabric.delete_fabric(fab_id)


@transaction.atomic
def add_fabric_switch(fab_id, data, user=""):
    serializer = SwitchPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    fabric.add_switches(fab_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def update_fabric_switch(fab_id, switch_id, data, user=""):
    serializer = FabricSwitchPutSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)
    fabric.update_switch(fab_id, switch_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def delete_fabric_switch(fab_id, switch_id, user=""):
    fabric.delete_switch(fab_id, switch_id, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def decommission_fabric_switch(fab_id, switch_id, user=""):
    fabric.decommission_switch(fab_id, switch_id, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def add_fabric_link(fab_id, data, user):
    serializer = LinkPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fabric.add_link(fab_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def update_fabric_link(fab_id, link_id, data, user):
    serializer = LinkPutSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fabric.update_link(fab_id, link_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def delete_fabric_link(fab_id, link_id, user=""):
    fabric.delete_link(fab_id, link_id, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@ transaction.atomic
def set_fabric_submit(fab_id, user=""):
    fabric.set_submit(fab_id, True, user)


@transaction.atomic
def update_fabric_defaults(fab_id, data, user=""):
    serializer = TopologyPostDefaultsSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fabric.update_defaults(fab_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def update_fabric_profiles(fab_id, data, user=""):
    serializer = FabricProfilesPutSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fabric.update_profiles(fab_id, serializer.data, user)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def build_fabric_config(fab_id):
    build.build_config(fab_id)
    serializer = FabricSerializer(fabric.get_fabric(fab_id))
    return serializer.data


@transaction.atomic
def clone_fabric(fab_id, data, user=""):
    serializer = CloneFabricSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    new_fab = fabric.clone_fabric(fab_id, data, user)
    serializer = FabricSerializer(new_fab)
    return serializer.data


@transaction.atomic
def discover_fabric_post(data):
    serializer = DiscoveryPostSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fab_id = fabric.create_empty_fabric(serializer.data)
    fabric.get_discovery(fab_id, serializer.data)
    fab = fabric.get_fabric(fab_id)
    serializer = FabricSerializer(fab)
    return serializer.data

@transaction.atomic
def save_discovered_fabric(fab_id, data, user=""):
    serializer = DiscoverySaveSerializer(data=data)
    if not serializer.is_valid():
        raise IgniteException(serializer.errors)

    fab = fabric.save_discovered_fabric(fab_id, data, user)
    serializer = DiscoveredFabricSerializer(fab)
    return serializer.data


@transaction.atomic
def delete_discovered_fabric(fab_id):
    fabric.delete_discovered_fabric(fab_id)


@transaction.atomic
def pull_switch_config(data, fid, sid, username=''):
    serializer = SwitchConfigSerializer(data=data)
    if not serializer.is_valid():
       raise IgniteException(serializer.errors)
    return switch_config.pull_switch_config(data, fid, sid, username)


def get_switch_config_latest(fid, sid):
    return switch_config.get_switch_config_latest(fid, sid)


@transaction.atomic
def reset_switch_boot_status(sw_id):
    serializer = FabricSerializer(fabric.reset_switch_boot_status(sw_id))
    return serializer.data


def get_switch_config_list(fid, sid):
    configs = switch_config.get_switch_config_list(fid, sid)
    serializer = SwitchConfigListSerializer(configs, many=True)
    return serializer.data


def get_switch_config(fid, sid, id):
    return switch_config.get_switch_config(fid, sid, id)
