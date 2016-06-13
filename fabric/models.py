from django.db import models

from bootstrap.models import SwitchBootDetail
from config.models import Profile as ConfigProfile
from discovery.models import DiscoveryRule
from feature.models import Profile as FeatureProfile
from image.models import ImageProfile
from switch.models import SwitchModel
from workflow.models import Workflow


class Topology(models.Model):

    name = models.TextField(unique=True)
    model_name = models.TextField()
    is_fabric = models.BooleanField(default=True)
    is_saved = models.BooleanField(default=True)
    is_discovered = models.BooleanField(default=False)
    submit = models.BooleanField(default=False)
    config_profile = models.ForeignKey(ConfigProfile, null=True, default=None,
                                       on_delete=models.PROTECT)
    feature_profile = models.ForeignKey(FeatureProfile, null=True, default=None,
                                       on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    build_time = models.DateTimeField(null=True, blank=True)
    updated_by = models.TextField(default="")


class Fabric(Topology):

    site = models.TextField(default="default")


class Switch(models.Model):

    topology = models.ForeignKey(Topology, null=True, default=None,
                                 on_delete=models.CASCADE)
    dummy = models.BooleanField(default=False)
    name = models.TextField()
    tier = models.TextField()
    serial_num = models.TextField(default="")
    mgmt_ip = models.TextField(blank=True, default="")
    model = models.ForeignKey(SwitchModel, null=True, default=None,
                              on_delete=models.PROTECT)
    image_profile = models.ForeignKey(ImageProfile, null=True, default=None,
                                      on_delete=models.PROTECT)
    config_profile = models.ForeignKey(ConfigProfile, null=True, default=None,
                                       on_delete=models.PROTECT)
    feature_profile = models.ForeignKey(FeatureProfile, null=True, default=None,
                                        on_delete=models.PROTECT)
    workflow = models.ForeignKey(Workflow, null=True, default=None,
                                 on_delete=models.PROTECT)
    boot_detail = models.ForeignKey(SwitchBootDetail, null=True, default=None,
                                    on_delete=models.PROTECT)
    config_type = models.TextField(default='POAP_CONFIG')


class Link(models.Model):

    topology = models.ForeignKey(Topology, on_delete=models.CASCADE)
    dummy = models.BooleanField(default=False)
    src_switch = models.ForeignKey(Switch, on_delete=models.CASCADE, null=True,
                                   default=None, related_name="link_src")
    dst_switch = models.ForeignKey(Switch, on_delete=models.CASCADE, null=True,
                                   default=None, related_name="link_dst")
    link_type = models.TextField()
    num_links = models.IntegerField()
    src_ports = models.TextField(default="")
    dst_ports = models.TextField(default="")


def generate_filename(self, filename):
    url = "switch/%s" % (self.name)
    return url


class SwitchConfig(models.Model):

    name = models.TextField(default=None)
    path = models.FileField(upload_to=generate_filename)
    switch = models.ForeignKey(Switch, null=True, default=None,
                                on_delete=models.CASCADE)
    version = models.IntegerField(null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
