from django.db.models import Q
import os
import re

from constants import *
from ignite.settings import REPO_PATH
from image.image_profile import get_profile
from models import Link, Switch, Topology
from switch.constants import BOTH, DOWNLINK, TIERS, UPLINK
from switch.switch import get_switch
from utils.exception import IgniteException
from utils.utils import ports_to_string, string_to_ports

import logging
logger = logging.getLogger(__name__)


class BaseTopology(object):

    _TIERS = list()
    _MANDATORY_TIERS = list()
    _ALLOWED_LINKS = list()
    _AUTO_LINKS = list()

    def __init__(self, top=None):
        self._top = top

    @staticmethod
    def create_object(model):
        if model == LEAF_SPINE:
            return LeafSpineTopology()

        raise IgniteException(ERR_INV_TOP_MODEL)

    @staticmethod
    def get_object(top_id, user=""):
        top = Topology.objects.get(pk=top_id)
        if user:
            top.updated_by = user
            top.save()

        if top.model_name == LEAF_SPINE:
            return LeafSpineTopology(top)

        raise IgniteException(ERR_INV_TOP_MODEL)

    @staticmethod
    def get_all_topologies(submit):
        if submit == TRUE:
            return Topology.objects.filter(is_fabric=False,
                                           submit=True).order_by(NAME)
        elif submit == FALSE:
            return Topology.objects.filter(is_fabric=False,
                                           submit=False).order_by(NAME)
        else:
            return Topology.objects.filter(is_fabric=False).order_by(NAME)

    def add_topology(self, data, user):
        logger.debug("topology name = %s, model = %s",
                     data[NAME], data[MODEL_NAME])

        self._validate_defaults(data[DEFAULTS])

        self._top = Topology()
        self._top.name = data[NAME]
        self._top.model_name = data[MODEL_NAME]
        self._top.is_fabric = False
        self._top.updated_by = user
        self._top.save()

        # defaults object
        self._top.defaults = dict()
        self._top.defaults[SWITCHES] = list()
        self._top.defaults[LINKS] = list()

        # add topology default switches with dummy=True
        for item in data[DEFAULTS][SWITCHES]:
            switch = Switch()
            switch.topology = self._top
            switch.dummy = True
            switch.name = DEFAULT
            switch.tier = item[TIER]
            switch.model = get_switch(item[MODEL])
            switch.image_profile = get_profile(item[IMAGE_PROFILE])
            switch.save()

            # add switch to topology defaults
            self._top.defaults[SWITCHES].append(switch)

        # add topology default links with dummy=True
        for item in data[DEFAULTS][LINKS]:
            link = Link()
            link.topology = self._top
            link.dummy = True
            link.src_ports = item[SRC_TIER]     # store tier name in ports
            link.dst_ports = item[DST_TIER]     # store tier name in ports
            link.link_type = item[LINK_TYPE]
            link.num_links = item[NUM_LINKS]
            link.save()

            # need tier names in link object while returning
            link.src_tier = link.src_ports
            link.dst_tier = link.dst_ports

            # add link to topology defaults
            self._top.defaults[LINKS].append(link)

        # new topology has no switches or links
        self._top.switches = list()
        self._top.links = list()

        return self._top

    def _validate_defaults(self, data):
        # TODO: validate defaults
        pass

    @staticmethod
    def get_topology(top_id):
        # get topology, its switches and links
        top = Topology.objects.get(pk=top_id)
        top.switches = Switch.objects.filter(topology_id=top_id,
                                             dummy=False).order_by(ID)
        top.links = Link.objects.filter(topology_id=top_id, dummy=False)

        # fill default switches & links in topology defaults
        top.defaults = dict()
        top.defaults[SWITCHES] = Switch.objects.filter(topology_id=top_id,
                                                       dummy=True).order_by(ID)
        top.defaults[LINKS] = list(Link.objects.filter(topology_id=top_id,
                                                       src_switch=None))

        for link in top.defaults[LINKS]:
            # need tier names in link object while returning
            link.src_tier = link.src_ports
            link.dst_tier = link.dst_ports

        return top

    @staticmethod
    def get_topology_detail(top_id):
        # get topology, its switches and links
        top = Topology.objects.get(pk=top_id)

        obj = dict()
        obj[SWITCHES] = list()
        obj[LINKS] = list()

        obj[ID] = top.id
        obj[NAME] = top.name

        for switch in Switch.objects.filter(topology_id=top_id, dummy=False):
            sw_obj = dict()
            sw_obj[ID] = switch.id
            sw_obj[NAME] = switch.name
            sw_obj[TIER] = switch.tier

            if switch.feature_profile:
                sw_obj[FEATURE_PROFILE] = switch.feature_profile.id
            else:
                default = Switch.objects.get(topology_id=top_id,
                                             tier=switch.tier, dummy=True)
                if default.feature_profile:
                    sw_obj[FEATURE_PROFILE] = default.feature_profile.id
                else:
                    sw_obj[FEATURE_PROFILE] = None

            obj[SWITCHES].append(sw_obj)

        for link in Link.objects.filter(topology_id=top_id, dummy=False):
            link_obj = dict()
            link_obj[ID] = link.id
            link_obj[SRC_SWITCH] = link.src_switch.id
            link_obj[DST_SWITCH] = link.dst_switch.id
            link_obj[LINK_TYPE] = link.link_type
            link_obj[NUM_LINKS] = link.num_links
            link_obj[SRC_PORTS] = link.src_ports
            link_obj[DST_PORTS] = link.dst_ports
            obj[LINKS].append(link_obj)

        return obj

    @staticmethod
    def update_topology_name(top_id, data, user):
        logger.debug("topology id = %d, name = %s", top_id, data[NAME])
        Topology.objects.filter(pk=top_id).update(name=data[NAME],
                                                  updated_by=user)

    @staticmethod
    def delete_topology(top_id):
        # check if any switch is booted
        if (Switch.objects.filter(topology_id=top_id,
                                  boot_detail__boot_status__isnull=False).count()):
            raise IgniteException(ERR_CANT_DEL_BOOTED_FABRIC)

        # cleanup for switches which have boot detail
        for switch in Switch.objects.filter(topology_id=top_id,
                                            boot_detail__isnull=False):
            BaseTopology._delete_switch(switch)

        Topology.objects.get(pk=top_id).delete()

    def add_switches(self, data):
        for item in data[SWITCHES]:
            if not item[COUNT]:
                continue

            # get next switch index for tier
            index = self._get_next_index(item[TIER])

            for ctr in range(item[COUNT]):
                self._add_switch(item[TIER], index + ctr)

    def _add_switch(self, tier, index=0):
        if not index:
            index = self._get_next_index(tier)

        # create new switch
        switch = Switch()
        switch.topology = self._top
        switch.dummy = False
        switch.tier = tier

        # get switch model from tier default
        default = Switch.objects.get(topology_id=self._top.id, tier=tier,
                                     dummy=True)
        switch.model = default.model

        # new switch name = fabric prefix (if any) + tier + index
        if self._top.is_fabric:
            switch.name = self._top.name + "_" + tier + str(index)
        else:
            switch.name = tier + str(index)

        switch.save()

        self._add_auto_links(switch)

    def _get_next_index(self, tier):
        # get all switches in tier
        switches = Switch.objects.filter(topology_id=self._top.id, tier=tier,
                                         dummy=False)

        # match with tier name followed by number like Leaf23 or Spine57
        regex = r'.*' + tier + '([1-9][0-9]*)$'
        index = 0

        # search for max index in tier name
        for switch in switches:
            match = re.match(regex, switch.name)

            if match:
                index = max(index, int(match.group(1)))

        logger.debug("tier = %s, next index = %d", tier, index+1)
        return index + 1

    def update_switch(self, switch_id, data):
        switch = Switch.objects.get(pk=switch_id)

        # TODO: check if model is valid, currently UI perform this check

        new_model = get_switch(data[MODEL])

        # is there a change in model?
        change = True if new_model != switch.model else False
        logger.debug("%schange in switch model", "no " if not change else "")

        # save new values
        switch.model = new_model
        switch.image_profile = (get_profile(data[IMAGE_PROFILE])
                                if data[IMAGE_PROFILE] else None)
        switch.save()

        if change:
            self.update_model(switch)

    def delete_switch(self, switch_id):
        switch = Switch.objects.get(pk=switch_id)
        if switch.boot_detail and switch.boot_detail.boot_status:
            raise IgniteException(ERR_CANT_DEL_BOOTED_SWITCH)

        BaseTopology._delete_switch(switch)

    @staticmethod
    def _delete_switch(switch):
        # delete switch and boot detail if any
        boot_detail = switch.boot_detail
        switch_id = switch.id
        switch.delete()
        if boot_detail:
            # delete build files if any
            try:
                os.remove(os.path.join(REPO_PATH, str(switch_id) + '.cfg'))
            except OSError:
                pass
            try:
                os.remove(os.path.join(REPO_PATH, str(switch_id) + '.yml'))
            except OSError:
                pass
            boot_detail.delete()

    def add_link(self, data):
        src_switch = Switch.objects.get(pk=data[SRC_SWITCH])
        dst_switch = Switch.objects.get(pk=data[DST_SWITCH])

        self._add_link(src_switch, dst_switch, data[LINK_TYPE], data[NUM_LINKS])

    def _add_link(self, src_switch, dst_switch, link_type, num_links,
                  src_ports=[], dst_ports=[]):
        # src_role is always DOWNLINK
        # dst_role is DOWNLINK for VPC links else UPLINK
        src_role = DOWNLINK
        dst_role = (DOWNLINK if link_type in [VPC_PEER, VPC_MEMBER] else UPLINK)

        # get ports on both switches
        src_ports = self._get_ports(src_switch, src_role, num_links, src_ports)
        dst_ports = self._get_ports(dst_switch, dst_role, num_links, dst_ports)

        logger.debug("src_ports = %s", src_ports)
        logger.debug("dst_ports = %s", dst_ports)

        # add new link
        self._add_link_to_db(link_type, num_links, src_switch, dst_switch,
                             src_ports, dst_ports)

    def _get_ports(self, switch, port_role, num_ports, ports=[]):
        logger.debug("switch id = %d, port_role = %s", switch.id, port_role)

        # get all links for switch
        links = Link.objects.filter(Q(src_switch_id=switch.id) |
                                    Q(dst_switch_id=switch.id),
                                    topology_id=self._top.id,
                                    dummy=False)

        used_ports = list()

        # make list of ports currently in use
        for link in links:
            if switch.id == link.src_switch.id:
                used_ports += string_to_ports(link.src_ports)
            else:
                used_ports += string_to_ports(link.dst_ports)

        # make list of ports available for port_role in switch model
        # first ports with exact port_role and then role=BOTH
        # available ports = model ports - used ports
        model_ports = switch.model.meta[port_role] + switch.model.meta[BOTH]
        avail_ports = [port for port in model_ports if port not in used_ports]

        logger.debug("model_ports = %s", ports_to_string(model_ports))
        logger.debug("used_ports = %s", ports_to_string(used_ports))
        logger.debug("avail_ports = %s", ports_to_string(avail_ports))

        # if ports are given, check that they are usable
        if ports:
            for port in ports:
                if port not in avail_ports:
                    raise IgniteException(ERR_INV_PORTS)
            return ports

        if num_ports > len(avail_ports):
            raise IgniteException(ERR_NOT_ENOUGH_PORTS)

        return avail_ports[:num_ports]

    def _add_link_to_db(self, link_type, num_links, src_switch, dst_switch,
                        src_ports, dst_ports):
        # create new link
        link = Link()
        link.topology = self._top
        link.dummy = False
        link.link_type = link_type
        link.num_links = num_links
        link.src_switch = src_switch
        link.dst_switch = dst_switch
        link.src_ports = ports_to_string(src_ports)
        link.dst_ports = ports_to_string(dst_ports)
        link.save()

        # create invidual physical links for matching with CDP data
        if num_links > 1 or link_type in [PORT_CHANNEL, VPC_PEER]:
            # set dummy = True for such links
            for index in range(num_links):
                link = Link()
                link.topology = self._top
                link.dummy = True
                link.link_type = PHYSICAL
                link.num_links = 1
                link.src_switch = src_switch
                link.dst_switch = dst_switch
                link.src_ports = src_ports[index]
                link.dst_ports = dst_ports[index]
                link.save()

    def update_link(self, link_id, data):
        src_ports = string_to_ports(data[SRC_PORTS])
        dst_ports = string_to_ports(data[DST_PORTS])

        # check that correct # of ports were given
        if (len(src_ports) != data[NUM_LINKS] or
                len(dst_ports) != data[NUM_LINKS]):
            raise IgniteException(ERR_INV_PORT_COUNT)

        # delete current link
        link = Link.objects.get(pk=link_id)
        src_switch = link.src_switch
        dst_switch = link.dst_switch
        self.delete_link(link_id, True)

        # add new link with new values
        self._add_link(src_switch, dst_switch, data[LINK_TYPE],
                       data[NUM_LINKS], src_ports, dst_ports)

    def _update_link_in_db(self, link, new_ports, is_src):
        old_src_ports = string_to_ports(link.src_ports)
        old_dst_ports = string_to_ports(link.dst_ports)

        # update ports in link
        if is_src:
            link.src_ports = ports_to_string(new_ports)
        else:
            link.dst_ports = ports_to_string(new_ports)

        link.save()

        if link.num_links > 1 or link.link_type in [PORT_CHANNEL, VPC_PEER]:
            # get member physical links
            for index in range(link.num_links):
                member = Link.objects.get(src_switch_id=link.src_switch.id,
                                          dst_switch_id=link.dst_switch.id,
                                          src_ports=old_src_ports[index],
                                          dst_ports=old_dst_ports[index],
                                          dummy=True)

                # update port
                if is_src:
                    member.src_ports = new_ports[index]
                else:
                    member.dst_ports = new_ports[index]

                member.save()
                index += 1

    def delete_link(self, link_id):
        link = Link.objects.get(pk=link_id)

        # delete physical links created for a logical link
        if link.num_links > 1 or link.link_type in [PORT_CHANNEL, VPC_PEER]:
            src_ports = string_to_ports(link.src_ports)
            dst_ports = string_to_ports(link.dst_ports)

            for index in range(link.num_links):
                Link.objects.filter(src_switch_id=link.src_switch.id,
                                    dst_switch_id=link.dst_switch.id,
                                    src_ports=src_ports[index],
                                    dst_ports=dst_ports[index]).delete()

        # delete the logical link
        link.delete()

    @staticmethod
    def set_submit(top_id, data, user):
        Topology.objects.filter(pk=top_id).update(submit=data, updated_by=user)

    @staticmethod
    def clear_topology(top_id, user):
        # delete all switches in topology except defaults
        # links get automatically deleted
        Switch.objects.filter(topology_id=top_id, dummy=False).delete()
        Topology.objects.filter(pk=top_id).update(updated_by=user)

    def update_defaults(self, data):
        self._validate_defaults(data)

        # update default switch attributes
        for item in data[SWITCHES]:
            try:
                switch = Switch.objects.get(topology_id=self._top.id,
                                            dummy=True, tier=item[TIER])
            except Switch.DoesNotExist:
                # if tier default does not exist, create one
                switch = Switch()
                switch.topology = self._top
                switch.dummy = True
                switch.name = DEFAULT
                switch.tier = item[TIER]

            switch.model = get_switch(item[MODEL])
            switch.image_profile = get_profile(item[IMAGE_PROFILE])
            switch.save()

        # update default link attributes
        for item in data[LINKS]:
            link = Link.objects.get(topology_id=self._top.id, dummy=True,
                                    src_ports=item[SRC_TIER],
                                    dst_ports=item[DST_TIER])
            link.link_type = item[LINK_TYPE]
            link.num_links = item[NUM_LINKS]
            link.save()


class LeafSpineTopology(BaseTopology):

    _TIERS = [SPINE, LEAF, CORE, BORDER]
    _MANDATORY_TIERS = [SPINE, LEAF]
    _ALLOWED_LINKS = [
        {SRC_TIER: SPINE, DST_TIER: LEAF, LINK_TYPE: [PHYSICAL, PORT_CHANNEL]},
        {SRC_TIER: LEAF, DST_TIER: LEAF, LINK_TYPE: [VPC_PEER, VPC_MEMBER]},
        {SRC_TIER: CORE, DST_TIER: SPINE, LINK_TYPE: [PHYSICAL, PORT_CHANNEL]},
        {SRC_TIER: LEAF, DST_TIER: BORDER, LINK_TYPE: [PHYSICAL, PORT_CHANNEL]},
    ]
    _AUTO_LINKS = [
        {SRC_TIER: SPINE, DST_TIER: LEAF, LINK_TYPE: [PHYSICAL, PORT_CHANNEL]},
    ]

    def __init__(self, top=None):
        super(LeafSpineTopology, self).__init__(top)

    def update_model(self, switch):
        # update links based on tier
        if switch.tier == CORE:
            self._update_core(switch)
        elif switch.tier == SPINE:
            self._update_spine(switch)
        elif switch.tier == LEAF:
            self._update_leaf(switch)
        elif switch.tier == BORDER:
            self._update_border(switch)

    def _update_core(self, switch):
        # get all links (only downlinks for core switch)
        links = (Link.objects.filter(topology_id=self._top.id,
                                     src_switch_id=switch.id,
                                     dummy=False).order_by("dst_switch__id"))

        # find ports on new model (downlink or both) & update
        model_ports = switch.model.meta[DOWNLINK] + switch.model.meta[BOTH]
        self._update_new_link_ports(links, model_ports, True)

    def _update_spine(self, switch):
        # get all downlinks on spine
        links = (Link.objects.filter(topology_id=self._top.id,
                                     src_switch_id=switch.id,
                                     dummy=False).order_by("dst_switch__id"))

        # find ports on new model (downlink or both) & update
        model_ports = switch.model.meta[DOWNLINK] + switch.model.meta[BOTH]
        used_count = self._update_new_link_ports(links, model_ports, True)

        # get all uplinks on spine
        links = (Link.objects.filter(topology_id=self._top.id,
                                     dst_switch_id=switch.id,
                                     dummy=False).order_by("src_switch__id"))

        # find ports on new model (uplink + remaining both)
        if used_count > len(switch.model.meta[DOWNLINK]):
            offset = used_count - len(switch.model.meta[DOWNLINK])
            model_ports = (switch.model.meta[UPLINK] +
                           switch.model.meta[BOTH][offset:])
        else:
            model_ports = switch.model.meta[UPLINK] + switch.model.meta[BOTH]

        # update ports on links
        self._update_new_link_ports(links, model_ports, False)

    def _update_leaf(self, switch):
        # get all leaf to spine links
        links = (Link.objects.filter(topology_id=self._top.id,
                                     dst_switch_id=switch.id,
                                     src_switch__tier=SPINE,
                                     dummy=False).order_by("src_switch__id"))

        # find ports on new model (uplink or both) & update
        model_ports = switch.model.meta[UPLINK] + switch.model.meta[BOTH]
        used_count = self._update_new_link_ports(links, model_ports, False)

        # get all leaf to leaf links where this switch is dst
        links = (Link.objects.filter(topology_id=self._top.id,
                                     dst_switch_id=switch.id,
                                     src_switch__tier=LEAF,
                                     dummy=False).order_by("src_switch__id"))

        # find ports on new model (downlink + remaining both)
        if used_count > len(switch.model.meta[UPLINK]):
            offset = used_count - len(switch.model.meta[UPLINK])
            model_ports = (switch.model.meta[DOWNLINK] +
                           switch.model.meta[BOTH][offset:])
        else:
            model_ports = switch.model.meta[DOWNLINK] + switch.model.meta[BOTH]

        # update ports on links
        used_count = self._update_new_link_ports(links, model_ports, False)

        # get all leaf to leaf links where this switch is src
        links = (Link.objects.filter(topology_id=self._top.id,
                                     src_switch_id=switch.id,
                                     dst_switch__tier=LEAF,
                                     dummy=False).order_by("dst_switch__id"))

        # delete used ports on model & update ports on new links
        model_ports[:] = model_ports[used_count:]
        used_count = self._update_new_link_ports(links, model_ports, True)

        # get all leaf to border links
        links = (Link.objects.filter(topology_id=self._top.id,
                                     src_switch_id=switch.id,
                                     dst_switch__tier=BORDER,
                                     dummy=False).order_by("dst_switch__id"))

        # delete used ports on model & update ports on new links
        model_ports[:] = model_ports[used_count:]
        self._update_new_link_ports(links, model_ports, True)

    def _update_border(self, switch):
        # get all links (only uplinks for border switch)
        links = (Link.objects.filter(topology_id=self._top.id,
                                     dst_switch_id=switch.id,
                                     dummy=False).order_by("src_switch__id"))

        # find ports on new model (uplink or both) & update
        model_ports = switch.model.meta[UPLINK] + switch.model.meta[BOTH]
        self._update_new_link_ports(links, model_ports, False)

    def _update_new_link_ports(self, links, ports, is_src):
        used_count = 0

        for link in links:
            # ran out of ports?
            if used_count + link.num_links > len(ports):
                raise IgniteException(ERR_NOT_ENOUGH_PORTS)

            # actual ports to be used in link
            new_ports = ports[used_count:used_count+link.num_links]

            logger.debug("link id = %d, %s, old_ports = %s, new ports = %s",
                         link.id, "src" if is_src else "dst",
                         link.src_ports if is_src else link.dst_ports,
                         ports_to_string(new_ports))

            # modify link with new ports
            self._update_link_in_db(link, new_ports, is_src)

            used_count += link.num_links

        return used_count

    def _add_auto_links(self, switch):
        logger.debug("switch id = %d, name = %s", switch.id, switch.name)

        # auto links only for Spine & Leaf switches
        if switch.tier not in [SPINE, LEAF]:
            return

        if switch.tier == SPINE:
            switch_port_role = DOWNLINK
            neigh_port_role = UPLINK
            neigh_list = Switch.objects.filter(topology_id=self._top.id,
                                               tier=LEAF,
                                               dummy=False).order_by(ID)
        else:
            switch_port_role = UPLINK
            neigh_port_role = DOWNLINK
            neigh_list = Switch.objects.filter(topology_id=self._top.id,
                                               tier=SPINE,
                                               dummy=False).order_by(ID)

        # get default link between Spine & Leaf
        link = Link.objects.get(topology_id=self._top.id, dummy=True,
                                src_ports=SPINE, dst_ports=LEAF)
        link_type = link.link_type
        num_links = link.num_links

        logger.debug("switch_port_role = %s, neigh_port_role = %s",
                     switch_port_role, neigh_port_role)
        logger.debug("link_type = %s, num_links = %d", link_type, num_links)

        for neigh in neigh_list:
            # gets ports on switch and then on neighbor
            switch_ports = self._get_ports(switch, switch_port_role, num_links)
            neigh_ports = self._get_ports(neigh, neigh_port_role, num_links)

            logger.debug("switch_ports = %s", switch_ports)
            logger.debug("neigh_ports = %s", neigh_ports)

            # add new link
            if switch.tier == SPINE:
                self._add_link_to_db(link_type, num_links, switch, neigh,
                                     switch_ports, neigh_ports)
            else:
                self._add_link_to_db(link_type, num_links, neigh, switch,
                                     neigh_ports, switch_ports)

    def delete_link(self, link_id, force=False):
        link = Link.objects.get(pk=link_id)

        # do not allow Spine-Leaf link to be deleted unless force=True
        if (not force and link.src_switch.tier == SPINE and
                link.dst_switch.tier == LEAF):
            raise IgniteException(ERR_LS_LINK_DEL_NOT_ALLOWED)

        super(LeafSpineTopology, self).delete_link(link_id)

    def update_defaults(self, data):
        # update the default values
        super(LeafSpineTopology, self).update_defaults(data)

        # TODO: reset topology with new defaults

    def get_all_switches(self, build=True):
        # if build is true, return only switches for whom config is built
        # else return all switches
        if build:
            return Switch.objects.filter(Q(tier=SPINE) | Q(tier=LEAF),
                                         topology_id=self._top.id, dummy=False)
        else:
            return Switch.objects.filter(topology_id=self._top.id, dummy=False)
