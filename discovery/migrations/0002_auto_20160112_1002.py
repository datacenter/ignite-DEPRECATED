# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0003_auto_20160104_1633'),
        ('workflow', '0001_initial'),
        ('discovery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='discoveryrule',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='image.ImageProfile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discoveryrule',
            name='workflow',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='workflow.Workflow', null=True),
            preserve_default=True,
        ),
    ]
