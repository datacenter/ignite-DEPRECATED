from django.db import models
from jsonfield import JSONField


class Task(models.Model):

    name = models.TextField(unique=True)
    handler = models.TextField(default='')
    function = models.TextField(default='')
    desc = models.TextField(default='')
    parameters = JSONField(default=[])
    location_server_ip = models.TextField(default='')
    location_server_user = models.TextField(null=True, default='')
    location_server_password = models.TextField(null=True, default='')
    location_access_protocol = models.TextField(default='')
    editable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
    ref_count = models.IntegerField(default=0)


class Workflow(models.Model):

    name = models.TextField(unique=True)
    submit = models.BooleanField(default=False)
    task_list = JSONField(default=[])
    editable = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
