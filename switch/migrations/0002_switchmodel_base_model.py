# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='switchmodel',
            name='base_model',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
