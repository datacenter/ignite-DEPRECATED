# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0002_switch_workflow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('username', models.TextField()),
                ('password', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GroupSwitch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(default=None, to='group.Group', null=True)),
                ('grp_switch', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='fabric.Switch', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('schedule', models.DateTimeField()),
                ('status', models.TextField(default=b'SCHEDULED', null=True, blank=True)),
                ('tasks', jsonfield.fields.JSONField(default=[])),
                ('task_id', models.TextField(blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
