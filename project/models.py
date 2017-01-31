from __future__ import unicode_literals

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator


class Project(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    description = models.TextField(verbose_name=_('Description'), null=True,
                                   blank=True)
    start_date = models.DateField(verbose_name=_('Start date'),
                                  default=timezone.now)
    end_date = models.DateField(verbose_name=_('End date'), null=True,
                                blank=True)
    is_active = models.BooleanField(verbose_name=_('Is active'), null=False,
                                    default=True)

    def __str__(self):
        return self.title


class Sprint(models.Model):
    NEW = 'new'
    ACTIVE = 'active'
    FINISHED = 'finished'
    SPRINT_STATUS_CHOICES = (
        (NEW, _('New')),
        (ACTIVE, _('Active')),
        (FINISHED, _('Finished'))
    )
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    team = models.ForeignKey('ProjectTeam')
    start_date = models.DateField(verbose_name=_('Start date'), null=True,
                                  blank=True)
    end_date = models.DateField(verbose_name=_('End date'), null=True,
                                blank=True)
    order = models.PositiveIntegerField(verbose_name=_('Order'), null=True,
                                        blank=True)
    status = models.CharField(verbose_name=_('Status'),
                              choices=SPRINT_STATUS_CHOICES, null=True,
                              blank=True, max_length=255)

    def __str__(self):
        return self.title


class Issue(models.Model):
    NEW = 'new'
    IN_PROGRESS = 'in progress'
    RESOLVED = 'resolved'
    ISSUE_STATUS_CHOICES = (
        (NEW, _('New')),
        (IN_PROGRESS, _('In Progress')),
        (RESOLVED, _('Resolved'))
    )
    root = models.ForeignKey('self', null=True, blank=True)
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    sprint = models.ForeignKey(Sprint, verbose_name=_('Sprint'),
                               null=True, blank=True)
    author = models.ForeignKey('employee.Employee', verbose_name=_('Author'),
                               related_name='author_issue_set')
    employee = models.ForeignKey('employee.Employee', verbose_name=_('Employee'),
                                 related_name='employee_issue_set', null=True,
                                 blank=True)
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    description = models.TextField(verbose_name=_('Description'), null=True,
                                   blank=True)
    status = models.CharField(verbose_name=_('Status'),
                              choices=ISSUE_STATUS_CHOICES, default=NEW,
                              null=True, blank=True, max_length=255)
    estimation = models.PositiveIntegerField(verbose_name=_('Estimation'),
                                             validators=[
                                                 MaxValueValidator(240)],
                                             null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.sprint and self.sprint.project != self.project:
            return ValidationError("Sprint is incorrect")
        super(Issue, self).save(*args, **kwargs)


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    employees = models.ManyToManyField('employee.Employee', verbose_name=_('Employees'))

    def __str__(self):
        return self.title


