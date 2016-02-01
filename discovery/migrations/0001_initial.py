# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20151230_1932'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscoveryRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('priority', models.IntegerField(default=1)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('subrules', jsonfield.fields.JSONField(default=[])),
                ('match', models.TextField(default=b'all')),
                ('updated_by', models.TextField(default=b'')),
                ('config', models.ForeignKey(to='config.Profile', on_delete=django.db.models.deletion.PROTECT)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
