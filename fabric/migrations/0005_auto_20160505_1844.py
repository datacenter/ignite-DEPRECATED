# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0004_auto_20160218_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='topology',
            name='is_discovered',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topology',
            name='is_saved',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
