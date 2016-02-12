from django.db import models
from discovery.models import DiscoveryRule


class SwitchBootDetail(models.Model):

    boot_status = models.TextField(null=True, default=None)
    match_type = models.TextField(default="")
    discovery_rule = models.IntegerField(default=0)
    serial_number = models.TextField(default="")
    boot_time = models.DateTimeField(null=True, default=None)
    build_time = models.DateTimeField(default=None)
    mgmt_ip = models.TextField(blank=True, default="")
