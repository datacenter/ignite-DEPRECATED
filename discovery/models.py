from django.db import models
from jsonfield import JSONField

from config.models import Profile
from image.models import ImageProfile
from workflow.models import Workflow


class DiscoveryRule(models.Model):

    name = models.TextField(unique=True)
    priority = models.IntegerField(default=1)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    config = models.ForeignKey(Profile, on_delete=models.PROTECT)
    image = models.ForeignKey(ImageProfile, null=True,
                              default=None, on_delete=models.PROTECT)
    workflow = models.ForeignKey(Workflow,  null=True,
                                 default=None, on_delete=models.PROTECT)
    subrules = JSONField(default=[])
    match = models.TextField(default="all")
    updated_by = models.TextField(default='')
