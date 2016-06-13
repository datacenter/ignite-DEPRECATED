# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0002_auto_20160113_0437'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='is_encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
