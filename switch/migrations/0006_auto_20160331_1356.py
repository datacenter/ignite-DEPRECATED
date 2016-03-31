# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('switch', '0005_auto_20160317_1656'),
    ]

    operations = [
        migrations.AlterField(
            model_name='switchmodel',
            name='meta',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='switchmodel',
            name='switch_data',
            field=jsonfield.fields.JSONField(default={}),
        ),
        migrations.AlterField(
            model_name='switchmodel',
            name='switch_info',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
