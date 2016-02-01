# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0003_auto_20151230_1953'),
    ]

    operations = [
        migrations.AddField(
            model_name='linecard',
            name='created',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='linecard',
            name='updated',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='switchmodel',
            name='created',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='switchmodel',
            name='updated',
            field=models.DateTimeField(default=datetime.date(2016, 1, 4), auto_now=True),
            preserve_default=False,
        ),
    ]
