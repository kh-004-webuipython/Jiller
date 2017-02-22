# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 18:06
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0005_auto_20170214_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='estimation',
            field=models.PositiveIntegerField(default=0, validators=[django.core.validators.MaxValueValidator(240)], verbose_name='Estimation'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='issue',
            name='type',
            field=models.CharField(choices=[('User_story', 'User story'), ('Task', 'Task'), ('Bug', 'Bug')], default='Task', max_length=255, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='projectnote',
            name='content',
            field=models.TextField(blank=True, max_length=5000, null=True, verbose_name='Note text'),
        ),
        migrations.AlterField(
            model_name='projectnote',
            name='title',
            field=models.CharField(blank=True, max_length=25, null=True, verbose_name='Title'),
        ),
    ]
