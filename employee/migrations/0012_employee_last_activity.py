# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 11:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employee', '0011_auto_20170221_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='last_activity',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Last activity'),
        ),
    ]
