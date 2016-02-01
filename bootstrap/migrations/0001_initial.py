# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SwitchBootDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('booted', models.BooleanField(default=False)),
                ('match_type', models.TextField(default=b'')),
                ('discovery_rule', models.IntegerField(default=0)),
                ('serial_number', models.TextField(default=b'')),
                ('boot_time', models.DateTimeField(default=None, null=True)),
                ('build_time', models.DateTimeField(default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
