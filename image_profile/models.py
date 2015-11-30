from django.db import models

# Create your models here.
class ImageProfile(models.Model):

    image_profile_name = models.TextField(unique=True)
    image = models.TextField()
    imageserver_ip = models.CharField(max_length=24)
    username= models.TextField()
    password = models.TextField()
    access_protocol = models.TextField()

