from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.core.exceptions import ValidationError
from datetime import date, datetime

from django.contrib.auth.models import AbstractUser
from simple_email_confirmation.models import SimpleEmailConfirmationUserMixin
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from sorl.thumbnail import get_thumbnail
from django.db.models.signals import pre_delete
from django.dispatch import receiver


@python_2_unicode_compatible
class Employee(SimpleEmailConfirmationUserMixin, AbstractUser):
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
        return datetime.strftime(self.date_joined, "%d.%m.%y")

    def get_cropped_photo(self, *args, **kwargs):
        return get_thumbnail(self.photo, '136x150', crop='center')

    @property
    def name(self):
        return '{} {}'.format(self.last_name, self.first_name)


# check for for PM teams before delete
@receiver(pre_delete, sender=Employee)
def delete_user_without_team(instance, **kwargs):
    from project.models import ProjectTeam
    team = ProjectTeam.objects.filter(employees=instance.id)

    team_list = ' '
    if instance.pm_role_access and team:
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
                                        auto_now_add=True)
    cost = models.FloatField(verbose_name=_('Cost'), validators=[MinValueValidator(0.0)])
    note = models.TextField(verbose_name=_('Note'), null=True, blank=True)

    def __str__(self):
        return "{} hours. {} - {}".format(self.cost, self.issue.title,
                                          self.user.get_full_name())
