# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bootstrap', '0004_auto_20160218_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='switchbootdetail',
            name='model_type',
            field=models.TextField(default=b''),
            preserve_default=True,
        ),
    ]
