from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from datetime import date, datetime

from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.core.validators import MaxValueValidator

from sorl.thumbnail import get_thumbnail


@python_2_unicode_compatible
class Employee(AbstractUser):
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
        return '{} {}'.format(self.first_name, self.last_name)


@python_2_unicode_compatible
class IssueLog(models.Model):
    issue = models.ForeignKey('project.Issue', verbose_name=_('Issue'))
    user = models.ForeignKey(Employee, verbose_name=_('Employee'))
    date_created = models.DateTimeField(verbose_name=_('Time'),
                                        auto_now_add=True)
    labor_costs = models.PositiveIntegerField(verbose_name=_('Labor costs'),
                                              validators=[
                                                  MaxValueValidator(240)], )
    note = models.TextField(verbose_name=_('Note'))

    def __str__(self):
        return "{} hours. {} - {}".format(self.labor_costs, self.issue.title,
                                          self.user.get_full_name())
