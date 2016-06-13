# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0005_auto_20160505_1844'),
        ('group', '0003_job_ctime'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='fabric',
            field=models.ForeignKey(default=None, to='fabric.Fabric', null=True),
            preserve_default=True,
        ),
    ]
