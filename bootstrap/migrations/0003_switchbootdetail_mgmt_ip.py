# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bootstrap', '0002_auto_20160112_1829'),
    ]

    operations = [
        migrations.AddField(
            model_name='switchbootdetail',
            name='mgmt_ip',
            field=models.TextField(default=b'', blank=True),
            preserve_default=True,
        ),
    ]
