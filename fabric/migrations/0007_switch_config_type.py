# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0006_switchconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='config_type',
            field=models.TextField(default=b'POAP_CONFIG'),
            preserve_default=True,
        ),
    ]
