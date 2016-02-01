# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0003_auto_20160104_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageprofile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
