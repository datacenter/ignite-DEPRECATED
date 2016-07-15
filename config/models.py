from django.db import models
from jsonfield import JSONField

from constants import CONFIGLET


def generate_groupname(self, filename):
    url = "configlets/%s-%s" % (self.name, str(self.version))
    return url


class ConfigletIndex(models.Model):
    name = models.TextField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')


class Configlet(models.Model):

    name = models.TextField()
    version = models.IntegerField(default=0)
    group = models.TextField()
    type = models.TextField(default=CONFIGLET)
    path = models.FileField(upload_to=generate_groupname)
    parameters = JSONField(default=[])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
    ref_count = models.IntegerField(default=0)
    configletindex = models.ForeignKey(ConfigletIndex, null=True, default=None,
                                       on_delete=models.CASCADE)


class ProfileIndex(models.Model):
    name = models.TextField(unique=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')


class Profile(models.Model):

    name = models.TextField()
    submit = models.BooleanField(default=False)
    version = models.IntegerField(default=0)
    construct_list = JSONField(default=[])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
    profileindex = models.ForeignKey(ProfileIndex, null=True, default=None,
                                     on_delete=models.CASCADE)
