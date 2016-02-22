# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bootstrap', '0003_switchbootdetail_mgmt_ip'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='switchbootdetail',
            name='build_time',
        ),
        migrations.RemoveField(
            model_name='switchbootdetail',
            name='mgmt_ip',
        ),
        migrations.RemoveField(
            model_name='switchbootdetail',
            name='serial_number',
        ),
    ]
