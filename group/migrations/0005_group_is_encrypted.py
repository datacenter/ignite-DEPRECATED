# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0004_group_fabric'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='is_encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
