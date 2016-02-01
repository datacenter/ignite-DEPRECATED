# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0002_imageprofile_updated_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageprofile',
            name='created',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='imageprofile',
            name='updated',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now=True),
            preserve_default=False,
        ),
    ]
