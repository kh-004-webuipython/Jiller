# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 21:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0010_auto_20170221_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectnote',
            name='picture',
            field=models.ImageField(blank=True, null=True, upload_to='notes/'),
        ),
        migrations.AlterField(
            model_name='projectnote',
            name='content',
            field=models.TextField(blank=True, max_length=10000, null=True, verbose_name='Note text'),
        ),
    ]