# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pool', '0003_auto_20160118_1301'),
    ]

    operations = [
        migrations.AddField(
            model_name='pool',
            name='role',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
