# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import fabric.models


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0005_auto_20160505_1844'),
    ]

    operations = [
        migrations.CreateModel(
            name='SwitchConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(default=None)),
                ('path', models.FileField(upload_to=fabric.models.generate_filename)),
                ('version', models.IntegerField(default=None, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
                ('switch', models.ForeignKey(default=None, to='fabric.Switch', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
