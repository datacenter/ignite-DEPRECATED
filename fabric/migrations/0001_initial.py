# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('config', '0002_auto_20151230_1932'),
        ('image', '0003_auto_20160104_1633'),
        ('feature', '0002_auto_20151230_1733'),
        ('bootstrap', '0001_initial'),
        ('switch', '0004_auto_20160104_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dummy', models.BooleanField(default=False)),
                ('link_type', models.TextField()),
                ('num_links', models.IntegerField()),
                ('src_ports', models.TextField(default=b'')),
                ('dst_ports', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Switch',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dummy', models.BooleanField(default=False)),
                ('name', models.TextField()),
                ('tier', models.TextField()),
                ('serial_num', models.TextField(default=b'')),
                ('boot_detail', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='bootstrap.SwitchBootDetail', null=True)),
                ('config_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='config.Profile', null=True)),
                ('feature_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='feature.Profile', null=True)),
                ('image_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='image.ImageProfile', null=True)),
                ('model', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=None, to='switch.SwitchModel', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Topology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(unique=True)),
                ('model_name', models.TextField()),
                ('is_fabric', models.BooleanField(default=True)),
                ('submit', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('updated_by', models.TextField(default=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Fabric',
            fields=[
                ('topology_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='fabric.Topology')),
                ('site', models.TextField(default=b'default')),
            ],
            options={
            },
            bases=('fabric.topology',),
        ),
        migrations.AddField(
            model_name='switch',
            name='topology',
            field=models.ForeignKey(default=None, to='fabric.Topology', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='dst_switch',
            field=models.ForeignKey(related_name=b'link_dst', default=None, to='fabric.Switch', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='src_switch',
            field=models.ForeignKey(related_name=b'link_src', default=None, to='fabric.Switch', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='link',
            name='topology',
            field=models.ForeignKey(to='fabric.Topology'),
            preserve_default=True,
        ),
    ]
