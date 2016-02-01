# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LineCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('lc_type', models.TextField()),
                ('lc_data', jsonfield.fields.JSONField()),
                ('lc_info', jsonfield.fields.JSONField()),
                ('ref_count', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SwitchModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('switch_type', models.TextField()),
                ('switch_data', jsonfield.fields.JSONField()),
                ('switch_info', jsonfield.fields.JSONField()),
                ('meta', jsonfield.fields.JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
