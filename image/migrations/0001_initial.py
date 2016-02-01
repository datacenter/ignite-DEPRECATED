# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ImageProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('profile_name', models.TextField(unique=True)),
                ('image_name', models.TextField()),
                ('image_server_ip', models.GenericIPAddressField(protocol=b'IPv4')),
                ('image_server_username', models.TextField()),
                ('image_server_password', models.TextField()),
                ('access_protocol', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
