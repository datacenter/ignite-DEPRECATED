# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageprofile',
            name='updated_by',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
