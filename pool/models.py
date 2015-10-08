__author__  = "arunrajms"

from django.db import models

# Create your models here.


class Pool(models.Model):

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    used = models.IntegerField(default=0)
    available = models.IntegerField(null=True)
    range = models.TextField(null=True)
    scope = models.CharField(max_length=16,default="global")
    

class PoolDetail(models.Model):

    index = models.ForeignKey(Pool)
    value = models.TextField()
    assigned = models.TextField()
    lastmodified = models.DateTimeField(auto_now=True)
    
class PoolFabricDetail(models.Model):
    pool_id = models.ForeignKey(Pool)
    value = models.TextField()
    fab_id = models.IntegerField(null=False,default=0)
    lastmodified = models.DateTimeField(auto_now=True)
    assigned = models.TextField()

    
