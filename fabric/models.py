from django.db import models
# Create your models here.
from django.utils import timezone

class Topology(models.Model):

    name = models.CharField(max_length=100, unique=True)
    topology_json = models.TextField()
    config_json = models.TextField()
    defaults = models.TextField()
    used = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    submit = models.CharField(max_length=10, default="false")

class Fabric(models.Model):

    name = models.CharField(max_length=100, unique=True)
    config_json = models.TextField()
    system_id = models.TextField()
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
    image_details = models.TextField()
    profiles = models.TextField()

class FabricRuleDB(models.Model):

    local_node = models.CharField(max_length=100)
    remote_node = models.CharField(max_length=100)
    remote_port = models.CharField(max_length=100)
    local_port = models.CharField(max_length=100)
    fabric =  models.ForeignKey('Fabric')
    action = models.IntegerField(default=-1)
    status = models.BooleanField(default=True)
    replica_num = models.IntegerField(default=0)


class DeployedFabricStats(models.Model):
    
    fabric_id = models.IntegerField(default= -1)
    replica_num = models.IntegerField(default = -1)
    switch_name = models.CharField(max_length=100)
    config_id = models.IntegerField(default=-1)
    booted = models.BooleanField(default=False)
    boot_time = models.DateTimeField(default=timezone.now)
    build_time = models.DateTimeField(default=timezone.now)
    config_name = models.CharField(max_length=100)
    discoveryrule_id = models.IntegerField(default=-1)
    system_id = models.CharField(max_length=100)
    match_type = models.CharField(max_length=100)
    configuration_generated = models.CharField(max_length=100)
    logs = models.CharField(max_length=100, default = 'logs')
