# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0004_auto_20160118_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageprofile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 21, 8, 51, 59, 271547), auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 21, 8, 51, 59, 271778), auto_now=True),
        ),
    ]
