# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0002_switchmodel_base_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='linecard',
            name='updated_by',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='switchmodel',
            name='updated_by',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
