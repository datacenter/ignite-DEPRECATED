# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feature', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feature',
            name='updated_by',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='updated_by',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
