# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 16:47
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('status', models.CharField(blank=True, choices=[('new', 'New'), ('in progress', 'In Progress'), ('resolved', 'Resolved')], default='new', max_length=255, null=True, verbose_name='Status')),
                ('estimation', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(240)], verbose_name='Estimation')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_issue_set', to=settings.AUTH_USER_MODEL, verbose_name='Author')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='employee_issue_set', to=settings.AUTH_USER_MODEL, verbose_name='Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('start_date', models.DateField(default=django.utils.timezone.now, verbose_name='Start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End date')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is active')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('employees', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Employees')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='Project')),
            ],
        ),
        migrations.CreateModel(
            name='Sprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start date')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End date')),
                ('order', models.PositiveIntegerField(blank=True, null=True, verbose_name='Order')),
                ('status', models.CharField(blank=True, choices=[('new', 'New'), ('active', 'Active'), ('finished', 'Finished')], max_length=255, null=True, verbose_name='Status')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='Project')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.ProjectTeam')),
            ],
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.Project', verbose_name='Project'),
        ),
        migrations.AddField(
            model_name='issue',
            name='root',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.Issue'),
        ),
        migrations.AddField(
            model_name='issue',
            name='sprint',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='project.Sprint', verbose_name='Sprint'),
        ),
    ]