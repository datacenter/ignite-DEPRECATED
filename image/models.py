from django.db import models

from datetime import datetime


class ImageProfile(models.Model):

    profile_name = models.TextField(unique=True)
    system_image = models.TextField(null=True, blank=True)
    epld_image = models.TextField(null=True, blank=True)
    kickstart_image = models.TextField(null=True, blank=True)
    image_server_ip = models.GenericIPAddressField(protocol='IPv4')
    image_server_username = models.TextField()
    image_server_password = models.TextField()
    access_protocol = models.TextField()
    updated_by = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True, default=datetime.utcnow())
    updated = models.DateTimeField(auto_now=True, default=datetime.utcnow())
