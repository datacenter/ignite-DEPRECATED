# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0006_auto_20160122_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageprofile',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='system_image',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='imageprofile',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
