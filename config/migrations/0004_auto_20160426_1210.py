# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0003_configlet_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='construct_list',
            field=jsonfield.fields.JSONField(default=[]),
        ),
    ]
