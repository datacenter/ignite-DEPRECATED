# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fabric', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('type', models.TextField()),
                ('scope', models.TextField()),
                ('start', models.TextField()),
                ('end', models.TextField()),
                ('updated_by', models.TextField(default=b'')),
                ('ref_count', models.IntegerField(default=0)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PoolEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('fabric', models.ForeignKey(default=None, to='fabric.Fabric', null=True)),
                ('pool', models.ForeignKey(to='pool.Pool')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
