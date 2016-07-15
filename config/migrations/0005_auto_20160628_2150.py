# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0004_auto_20160426_1210'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigletIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProfileIndex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='configlet',
            name='configletindex',
            field=models.ForeignKey(default=None, to='config.ConfigletIndex', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='configlet',
            name='version',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='profileindex',
            field=models.ForeignKey(default=None, to='config.ProfileIndex', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='version',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='configlet',
            name='name',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.TextField(),
        ),
    ]
