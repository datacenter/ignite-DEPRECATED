from django.db import models
from jsonfield import JSONField

from fabric.models import Fabric, Switch


class Pool(models.Model):

    name = models.TextField(unique=True)
    type = models.TextField()
    scope = models.TextField()
    blocks = JSONField(default=[])
    updated_by = models.TextField(default='')
    ref_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class PoolEntry(models.Model):

    pool = models.ForeignKey(Pool, on_delete=models.CASCADE)
    fabric = models.ForeignKey(Fabric, on_delete=models.CASCADE,
                               null=True, default=None)
    value = models.TextField()
    switch = models.ForeignKey(Switch, null=True, default=None,
                                 on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
