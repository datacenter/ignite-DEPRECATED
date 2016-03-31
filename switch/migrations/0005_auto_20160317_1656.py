# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0004_auto_20160104_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='switchmodel',
            name='boot_in_progress',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='switchmodel',
            name='booted_with_fail',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='switchmodel',
            name='booted_with_success',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
