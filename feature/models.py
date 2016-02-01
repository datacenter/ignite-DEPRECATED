from django.db import models
from jsonfield import JSONField


def generate_groupname(self, filename):
    url = "features/%s" % (self.name)
    return url


class Feature(models.Model):
    name = models.TextField(unique=True)
    path = models.FileField(upload_to=generate_groupname)
    ref_count = models.IntegerField(default=0)
    parameters = JSONField(default=[])
    group = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')


class Profile(models.Model):
    name = models.TextField(unique=True)
    submit = models.BooleanField(default=False)
    construct_list = JSONField(default=[])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')
