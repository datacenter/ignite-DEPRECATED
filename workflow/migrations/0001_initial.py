# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('handler', models.TextField(default=b'')),
                ('function', models.TextField(default=b'')),
                ('desc', models.TextField(default=b'')),
                ('parameters', jsonfield.fields.JSONField(default=[])),
                ('location_server_ip', models.TextField(default=b'')),
                ('location_server_user', models.TextField(default=b'', null=True)),
                ('location_server_password', models.TextField(default=b'', null=True)),
                ('location_access_protocol', models.TextField(default=b'')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
                ('ref_count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workflow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('submit', models.BooleanField(default=False)),
                ('task_list', jsonfield.fields.JSONField(default=[])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
