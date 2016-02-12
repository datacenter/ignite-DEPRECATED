# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_configlet_type'),
        ('feature', '0002_auto_20151230_1733'),
        ('fabric', '0002_switch_workflow'),
    ]

    operations = [
        migrations.AddField(
            model_name='topology',
            name='config_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='config.Profile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topology',
            name='feature_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='feature.Profile', null=True),
            preserve_default=True,
        ),
    ]
