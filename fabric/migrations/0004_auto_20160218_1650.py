# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0003_auto_20160210_1237'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='mgmt_ip',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topology',
            name='build_time',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
