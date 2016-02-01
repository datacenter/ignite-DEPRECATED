from django.db import models
from django.contrib.auth.models import User


class AAAServer(models.Model):
    server_ip = models.TextField(unique=True, default='')
    port = models.IntegerField(default=0)
    secret = models.TextField(default='')
    protocol = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    updated_by = models.TextField(default='')


class AAAUser(models.Model):
    username = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)
