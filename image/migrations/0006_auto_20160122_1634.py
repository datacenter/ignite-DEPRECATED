# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0005_auto_20160121_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageprofile',
            name='epld_image',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imageprofile',
            name='kickstart_image',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='imageprofile',
            old_name='image_name',
            new_name='system_image',
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 22, 11, 4, 8, 934532), auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='updated',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 22, 11, 4, 8, 934563), auto_now=True),
        ),
    ]
