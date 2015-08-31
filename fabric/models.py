from django.db import models
# Create your models here.

class Topology(models.Model):

    name = models.CharField(max_length=100, unique=True)
    topology_json = models.TextField()
    config_json = models.TextField()
    used = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    submit = models.CharField(max_length=10, default="false")

class Fabric(models.Model):

    name = models.CharField(max_length=100, unique=True)
    config_json = models.TextField()
    locked = models.BooleanField(default=True)
    validate = models.BooleanField(default=True)
    instance = models.IntegerField(default = 1)
    topology = models.ForeignKey('Topology')
    booted = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    submit = models.CharField(max_length=10, default="false")


class FabricRuleDB(models.Model):

    local_node = models.CharField(max_length=100)
    remote_node = models.CharField(max_length=100)
    remote_port = models.CharField(max_length=100)
    local_port = models.CharField(max_length=100)
    fabric =  models.ForeignKey('Fabric')
    action = models.IntegerField(default=-1)
    status = models.BooleanField(default=True)
