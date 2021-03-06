# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 00:15
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_auto_20170208_2133'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('content', models.TextField(blank=True, null=True, verbose_name='Note text')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='Project')),
            ],
        ),
    ]
