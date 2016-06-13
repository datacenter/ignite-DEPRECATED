from django.db import models

from fabric.models import Fabric, Switch
from image.models import ImageProfile
from jsonfield import JSONField


class Group(models.Model):

    name = models.TextField(unique=True, blank=False)
    username = models.TextField(blank=False)
    password = models.TextField(blank=False)
    is_encrypted = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
    ref_count = models.IntegerField(default=0)
    fabric = models.ForeignKey(Fabric, null=True, default=None,
                               on_delete=models.CASCADE)


class GroupSwitch(models.Model):

    group = models.ForeignKey(Group, null=True, default=None,
                              on_delete=models.CASCADE)
    grp_switch = models.ForeignKey(Switch, null=True, default=None,
                                   on_delete=models.PROTECT)


class Job(models.Model):

    name = models.TextField(unique=True, blank=False)
    schedule = models.DateTimeField(blank=False)
    status = models.TextField(default="SCHEDULED", null=True, blank=True)
    tasks = JSONField(default=[])
    task_id = models.TextField(blank=True)
    ctime = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
