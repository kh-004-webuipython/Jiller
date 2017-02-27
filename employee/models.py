from __future__ import unicode_literals
from datetime import date, datetime, timedelta as td

from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils import formats
# from django.utils.dateparse import parse_date
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import AbstractUser
from django.db import models

from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin
from sorl.thumbnail import get_thumbnail

from project.models import ProjectTeam, Project


@python_2_unicode_compatible
class Employee(SimpleEmailConfirmationUserMixin, AbstractUser):
    date_birth = models.DateField(verbose_name=_('Date birth'), null=True,
                                  blank=True)
    photo = models.ImageField(upload_to='avatars/', null=True, blank=True)
    last_activity = models.DateTimeField(verbose_name=_('Last activity'), null=True,
                                         blank=True)

    def get_all_projects(self):
        return Project.objects.get_user_projects(
            self).order_by('-start_date')

    def __str__(self):
        return self.username

    def online_status(self):
        status = None
        now = timezone.now()
        moreThanDayGap = now - td(hours=24)
        moreThanHourGap = now - td(hours=1)
        gap = now - td(seconds=900)
        if not self.last_activity:
            status = 'Never logged in'
        elif self.last_activity < moreThanDayGap or now.day > timezone.localtime(self.last_activity).day:
            status = 'last seen ' + str(formats.date_format(timezone.localtime(
                self.last_activity), 'DATE_FORMAT')) + ' at ' \
                     + str(formats.date_format(timezone.localtime(
                self.last_activity), 'TIME_FORMAT'))
        elif self.last_activity < moreThanHourGap:
            status = 'last seen today at ' + str(formats.date_format(timezone.localtime(
                self.last_activity), 'TIME_FORMAT'))
        elif self.last_activity <= gap:
            delta = now - self.last_activity
            status = 'last seen ' + str(td(seconds=delta.seconds).seconds / 60) + ' minutes ago'
        elif self.last_activity > gap:
            status = 'Online'

        return status

    def calculate_age(self):
        if self.date_birth:
            today = date.today()
            return today.year - self.date_birth.year - (
                (today.month, today.day) < (self.date_birth.month,
                                            self.date_birth.day))
        return False

    def get_pretty_date_joined(self):
        return datetime.strftime(self.date_joined, "%d.%m.%y")

    def get_cropped_photo(self, *args, **kwargs):
        return get_thumbnail(self.photo, '136x150', crop='center')

    @property
    def get_role(self):
        return self.groups.first() or 'admin'


# check users for for PM teams before delete
@receiver(pre_delete, sender=Employee)
def check_delete_user_in_team(instance, **kwargs):
    from project.models import ProjectTeam
    team = ProjectTeam.objects.filter(employees=instance.id)
    team_list = ' '
    if instance in Employee.objects.filter(groups=4) and team:
        for cur_team in team:
            team_list += '"' + str(cur_team) + '", '
        team_list = team_list[:len(team_list) - 2]
        raise ValidationError(
            "This user can not be deleted, it has next team(s):" + team_list)


@python_2_unicode_compatible
class IssueLog(models.Model):
    issue = models.ForeignKey('project.Issue', verbose_name=_('Issue'))
    user = models.ForeignKey(Employee, verbose_name=_('Employee'))
    date_created = models.DateTimeField(verbose_name=_('Time'),
                                        default=timezone.now)
    cost = models.FloatField(verbose_name=_('Cost'), default=0, validators=[MinValueValidator(0.0)])
    note = models.TextField(verbose_name=_('Note'), null=True, blank=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return "{} hours. {} - {}".format(self.cost, self.issue.title,
                                          self.user.get_full_name())

    def get_pretty_date_created(self):
        return datetime.strftime(self.date_created, "%d.%m.%y %H:%M")

    class Meta:
        ordering = ['-date_created']
