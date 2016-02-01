# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='editable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='workflow',
            name='editable',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
