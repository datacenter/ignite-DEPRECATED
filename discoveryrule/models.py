__author__  = "arunrajms"

from django.db import models

# Create your models here.

class DiscoveryRule(models.Model):

    name = models.CharField(max_length=100)
    priority = models.IntegerField(default=1)
    used_count = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    config_id = models.IntegerField(default=0)
    subrules = models.TextField()
    match = models.CharField(max_length=10,default="all")
    fabric_id = models.IntegerField(default= -1)
    replica_num = models.IntegerField(default= -1)
    switch_name = models.CharField(max_length=100,default=' ')
