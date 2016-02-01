# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0002_poolentry_switch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pool',
            name='end',
        ),
        migrations.RemoveField(
            model_name='pool',
            name='start',
        ),
        migrations.AddField(
            model_name='pool',
            name='blocks',
            field=jsonfield.fields.JSONField(default=[]),
            preserve_default=True,
        ),
    ]
