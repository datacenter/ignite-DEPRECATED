from django.db import models
from jsonfield import JSONField

from constants import CONFIGLET


def generate_groupname(self, filename):
    url = "configlets/%s" % (self.name)
    return url


class Configlet(models.Model):

    name = models.TextField(unique=True)
    group = models.TextField()
    type = models.TextField(default=CONFIGLET)
    path = models.FileField(upload_to=generate_groupname)
    parameters = JSONField(default=[])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
    ref_count = models.IntegerField(default=0)


class Profile(models.Model):

    name = models.TextField(unique=True)
    submit = models.BooleanField(default=False)
    construct_list = JSONField(default=[])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
