# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-18 20:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0006_auto_20170217_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sprint',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Start date'),
        ),
    ]
