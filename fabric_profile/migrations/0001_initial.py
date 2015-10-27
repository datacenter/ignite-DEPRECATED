# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import fabric_profile.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FabricProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('submit', models.CharField(default=b'false', max_length=10)),
                ('referenced', models.IntegerField(default=0, null=True, blank=True)),
                ('installed', models.IntegerField(default=0, null=True, blank=True)),
                ('construct_list', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('used', models.IntegerField(default=0)),
                ('last_modified_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProfileTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('config_path', models.FileField(upload_to=fabric_profile.models.generate_groupname)),
                ('parameters', models.TextField()),
                ('status', models.BooleanField(default=True)),
                ('group', models.CharField(max_length=100)),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
