from django.db import models
from jsonfield import JSONField


class LineCard(models.Model):

    name = models.TextField(unique=True)
    lc_type = models.TextField()
    lc_data = JSONField()
    lc_info = JSONField()
    updated_by = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ref_count = models.IntegerField(default=0)


class SwitchModel(models.Model):

    name = models.TextField(unique=True)
    base_model = models.TextField(default="")
    switch_type = models.TextField()
    switch_data = JSONField(default={})
    switch_info = JSONField(default={})
    booted_with_success = models.IntegerField(default=0)
    booted_with_fail = models.IntegerField(default=0)
    boot_in_progress = models.IntegerField(default=0)
    meta = JSONField(default={})
    updated_by = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
