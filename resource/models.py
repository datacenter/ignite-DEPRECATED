__author__  = "arunrajms"

from django.db import models

class Switch(models.Model):

    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    slots = models.IntegerField(default=0)
    tier = models.CharField(max_length=100)
    image = models.TextField()
    line_cards = models.TextField()