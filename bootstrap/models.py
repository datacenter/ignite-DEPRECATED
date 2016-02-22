from django.db import models
from discovery.models import DiscoveryRule


class SwitchBootDetail(models.Model):

    boot_status = models.TextField(null=True, default=None)
    match_type = models.TextField(default="")
    discovery_rule = models.IntegerField(default=0)
    boot_time = models.DateTimeField(null=True, default=None)
