# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0007_auto_20160201_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageprofile',
            name='is_encrypted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
