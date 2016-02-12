# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20151230_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='configlet',
            name='type',
            field=models.TextField(default=b'configlet'),
            preserve_default=True,
        ),
    ]
