# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0002_switch_workflow'),
        ('pool', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='poolentry',
            name='switch',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='fabric.Switch', null=True),
            preserve_default=True,
        ),
    ]
