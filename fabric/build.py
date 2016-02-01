from django.utils import timezone
import os
import yaml

from autonetkit.start_ank import run_ank
from bootstrap.models import SwitchBootDetail
from config.profile import build_config_profile
from config.constants import HOST_NAME
from constants import *
import fabric
from feature.feature import build_feature_profile
from ignite.settings import REPO_PATH
from models import Fabric
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
        try:
            os.remove(os.path.join(REPO_PATH + str(switch.id) + '.cfg'))
        except OSError as e:
            pass

    # build config on each switch in fabric
    _build_fabric_config(fab_id, switches)
    for switch in switches:
        logger.debug('Starting build config (Dry-run/non ANK) for switch %s'
                     % switch.name)

        # fetch switch config profile
        cfg = fabric.get_switch_config_profile(switch)
        cfg_file = os.path.join(REPO_PATH + str(switch.id) + '.cfg')

        if cfg:
            logger.debug("Config profile for %s = %s", switch.name, cfg.name)
            logger.debug("Build config")

            with open(cfg_file, 'a') as output_fh:
                output_fh.write(build_config_profile(cfg, switch))

        # fetch switch workflow
        wf = fabric.get_switch_workflow(switch)

        # fetch switch image
        image = fabric.get_switch_image(switch)

        logger.debug("Build workflow")
        wf_file = os.path.join(REPO_PATH + str(switch.id) + '.yml')

        with open(wf_file, 'w') as output_fh:
            output_fh.write(yaml.safe_dump(build_workflow(wf, image, cfg_file),
                                           default_flow_style=False))

        if not switch.boot_detail:
            boot_detail = SwitchBootDetail()
            boot_detail.build_time = timezone.now()
            boot_detail.save()
            switch.boot_detail = boot_detail
            switch.save()
        else:
            switch.boot_detail.build_time = timezone.now()
            switch.boot_detail.save()


def _build_fabric_config(fab_id, switches):
    profiles = []
    generated_prof = []

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
        device_profile = {'profiles': profiles}
        topo_detail = fabric.get_topology_detail(fab_id)
        run_ank(topo_detail=topo_detail, prof_detail=device_profile)


def get_instance_value(param_name, switch, switch_name):
    if param_name == HOST_NAME:
        if switch:
            return switch.name
        return switch_name

    return None
