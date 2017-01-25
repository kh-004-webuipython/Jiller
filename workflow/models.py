from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator
from datetime import date, datetime
from sorl.thumbnail import get_thumbnail


class Employee(AbstractUser):
    DEVELOPER = 'developer'
    PRODUCT_OWNER = 'product owner'
    SCRUM_MASTER = 'scrum master'
    EMPLOYEE_ROLES_CHOICES = (
        (DEVELOPER, _('Developer')),
        (PRODUCT_OWNER, _('Product Owner')),
        (SCRUM_MASTER, _('Scrum Master'))
    )

    role = models.CharField(max_length=255, choices=EMPLOYEE_ROLES_CHOICES,
                            verbose_name=_('Role'))
    date_birth = models.DateField(verbose_name=_('Date birth'), null=True,
                                  blank=True)
    photo = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

    def calculate_age(self):
        if self.date_birth:
            today = date.today()
            return today.year - self.date_birth.year - (
                (today.month, today.day) < (self.date_birth.month,
                                            self.date_birth.day))
        return False

    def get_pretty_date_joined(self):
        return datetime.strftime(self.date_joined, "%d/%m/%y")

    def get_cropped_photo(self, *args, **kwargs):
        return get_thumbnail(self.photo, '136x150', crop='center')


class Project(models.Model):
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    description = models.TextField(verbose_name=_('Description'), null=True,
                                   blank=True)
    start_date = models.DateField(verbose_name=_('Start date'),
                                  auto_now_add=True)
    end_date = models.DateField(verbose_name=_('End date'), null=True,
                                blank=True)

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
    project = models.ForeignKey(Project)
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
    project = models.ForeignKey(Project, null=True, blank=True)
    sprint = models.ForeignKey(Sprint, verbose_name=_('Sprint'))
    author = models.ForeignKey(Employee, verbose_name=_('Author'),
                               related_name='author_issue_set')
    employee = models.ForeignKey(Employee, verbose_name=_('Employee'),
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
        if self.sprint.project != self.project:
            return ValidationError("Sprint is incorrect")
        super(Issue, self).save(*args, **kwargs)


class ProjectTeam(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('Project'))
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    employees = models.ManyToManyField(Employee, verbose_name=_('Employees'))

    def __str__(self):
        return self.title


class IssueLog(models.Model):
    issue = models.ForeignKey(Issue, verbose_name=_('Issue'))
    user = models.ForeignKey(Employee, verbose_name=_('Employee'))
    date_created = models.DateTimeField(verbose_name=_('Time'),
                                        auto_now_add=True)
    labor_costs = models.PositiveIntegerField(verbose_name=_('Labor costs'),
                                              validators=[
                                                  MaxValueValidator(240)], )
    note = models.TextField(verbose_name=_('Note'))

    def __str__(self):
        return "{} hours. {} - {}".format(self.labor_costs, self.issue.title,
                                          self.user.get_full_name)
