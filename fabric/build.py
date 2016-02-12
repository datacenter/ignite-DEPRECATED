from django.utils import timezone
import os
import yaml

from autonetkit.start_ank import run_ank
import bootstrap
from bootstrap.models import SwitchBootDetail
from config.profile import build_config_profile
from config.constants import HOST_NAME, VPC_PEER_SRC, VPC_PEER_DST, \
    VPC_PEER_PORTS, UPLINK_PORTS, DOWNLINK_PORTS
from constants import *
import fabric
from feature.feature import build_feature_profile
from ignite.settings import REPO_PATH
from models import Fabric
from pool.pool import get_peer_mgmt_ip
from switch.constants import BOTH, UPLINK, DOWNLINK
from topology import BaseTopology
from utils.exception import IgniteException
from workflow.workflow import build_workflow

import logging
logger = logging.getLogger(__name__)


def build_config(fab_id):
    fab = Fabric.objects.get(pk=fab_id)
    if not fab.submit:
        raise IgniteException(ERR_BUILD_WITHOUT_SUBMIT)

    # get all switches in fabric
    switches = fabric.get_all_switches(fab_id)

    for switch in switches:
        bootstrap.bootstrap.update_boot_detail(switch,
                                               build_time=timezone.now())
        try:
            os.remove(os.path.join(REPO_PATH + str(switch.id) + '.cfg'))
        except OSError as e:
            pass

    # Run ANK
    device_profile = _build_ank_profiles(fab.feature_profile, switches)

    if device_profile:
        topo_detail = fabric.get_topology_detail(fab_id)
        run_ank(topo_detail=topo_detail, prof_detail=device_profile)
        bootstrap.bootstrap.update_boot_detail(switch,
                                               build_time=timezone.now())

    # fetch fabric level config
    fab_cfg = fab.config_profile

    # build config on each switch in fabric
    for switch in switches:
        build_switch_config(switch, fab_cfg=fab_cfg)


def build_switch_config(switch, fab_cfg=None, switch_cfg=None):

    if switch.topology:

        if not switch.topology.submit:
            raise IgniteException(ERR_REQUEST_WITHOUT_SUBMIT)

    logger.debug('Starting build config for switch %s' % switch.name)

    # delete cfg file when matching in discovery rule
    if not switch.topology:
        try:
            os.remove(os.path.join(REPO_PATH + str(switch.id) + '.cfg'))
        except OSError as e:
            pass

    if not switch_cfg:
        # fetch switch config profile
        switch_cfg = fabric.get_switch_config_profile(switch)

	if switch_cfg:
	    logger.debug("Config profile for %s- %s" % (switch.name,
                                                        switch_cfg.name))
	else:
	    logger.debug("No switch level config profile applied for- %s"
                         % switch.name)

        if not fab_cfg:
            fab_cfg = switch.topology.config_profile

            if fab_cfg:
                logger.debug("Fabric level config profile for- %s", fab_cfg.name)
            else:
                logger.debug("No fabric level config profile applied")

    cfg_file = os.path.join(REPO_PATH + str(switch.id) + '.cfg')

    if fab_cfg or switch_cfg:
        bootstrap.bootstrap.update_boot_detail(switch,
                                               build_time=timezone.now())

        with open(cfg_file, 'a') as output_fh:
            output_fh.write(build_config_profile([fab_cfg, switch_cfg], switch))


def _build_ank_profiles(fab_feature_prof, switches):
    device_profile = {}
    profiles = []
    generated_prof = []

    if fab_feature_prof:
        device_profile.update({'fabric_profile':
                              build_feature_profile(fab_feature_prof)})

    for switch in switches:
        logger.debug('Processing switch %s' % switch.name)

        feature_prof = fabric.get_switch_feature_profile(switch)

        if not feature_prof:
            logger.debug("No feature profile for %s", switch.name)
            continue

        logger.debug("Feature profile for %s = %s", switch.name,
                     feature_prof.name)

        if feature_prof.id not in generated_prof:
            generated_prof.append(feature_prof.id)
            profiles.append(build_feature_profile(feature_prof))

    if profiles:
        device_profile.update({'profiles': profiles})

    return device_profile


def get_instance_value(instance_value, switch, switch_name):
    logger.debug("Get Instance value for %s" % instance_value)

    if instance_value == HOST_NAME:
        if switch:
            return switch.name
        return switch_name

    if instance_value == VPC_PEER_SRC:

        if not (switch.boot_detail or switch.boot_detail.mgmt_ip):
            raise IgniteException("%s- %s"
                                  % (ERR_MGMT_IP_NOT_DETERMINED,
                                     switch.name))

        return switch.boot_detail.mgmt_ip

    if not switch.topology:
        raise IgniteException("%s- %s"
                              % (ERR_SWITCH_FABRIC_NOT_DETERMINED,
                                 switch.name))

    topo = BaseTopology.get_object(switch.topology.id)

    if instance_value == VPC_PEER_DST:
        peer_switch = topo.get_vpc_peer_switch(switch)

        if not peer_switch.boot_detail:

            if not (switch.boot_detail or switch.boot_detail.mgmt_ip):
                raise IgniteException("%s- %s"
                                      % (ERR_MGMT_IP_NOT_DETERMINED,
                                         switch.name))

            return get_peer_mgmt_ip(switch, peer_switch)
        else:

            if not peer_switch.boot_detail.mgmt_ip:
                raise IgniteException("%s- %s"
                                      % (ERR_PEER_MGMT_IP_NOT_DETERMINED,
                                         switch.name))
            return peer_switch.boot_detail.mgmt_ip

    if instance_value == VPC_PEER_PORTS:
        return (topo.get_vpc_peer_ports(switch))

    if instance_value == UPLINK_PORTS:
        return (topo.get_uplink_ports(switch))

    if instance_value == DOWNLINK_PORTS:
        return (topo.get_downlink_ports(switch))

    raise IgniteException("%s- %s Instance %s"
                          % (ERR_FAILED_TO_GET_INSTANCE_PARAM_VALUE,
                             switch.name, instance_value))
