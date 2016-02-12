# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0002_group_ref_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='ctime',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
