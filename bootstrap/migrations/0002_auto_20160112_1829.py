# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bootstrap', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='switchbootdetail',
            name='booted',
        ),
        migrations.AddField(
            model_name='switchbootdetail',
            name='boot_status',
            field=models.TextField(default=None, null=True),
            preserve_default=True,
        ),
    ]
