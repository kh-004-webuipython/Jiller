from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _
from datetime import date, datetime

from django.db import models
from sorl.thumbnail import get_thumbnail

from django.contrib.auth.models import AbstractUser


class Employee(AbstractUser):
    DEVELOPER = 'developer'
    PRODUCT_OWNER = 'product owner'
    SCRUM_MASTER = 'scrum master'
    EMPLOYEE_ROLES_CHOICES = (
        (DEVELOPER, _('Developer')),
        (PRODUCT_OWNER, _('Product Owner')),
        (SCRUM_MASTER, _('Scrum Master'))
    )

    role = models.CharField(max_length=255, choices=EMPLOYEE_ROLES_CHOICES, verbose_name=_('Role'))
    date_birth = models.DateField(verbose_name=_('Date birth'), null=True, blank=True)
    photo = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.username

    def calculate_age(self):
        if self.date_birth:
            today = date.today()
            return today.year - self.date_birth.year - (
                (today.month, today.day) < (self.date_birth.month, self.date_birth.day))
        return False

    def get_pretty_date_joined(self):
        return datetime.strftime(self.date_joined, "%d/%m/%y")

    def get_cropped_photo(self, *args, **kwargs):
        return get_thumbnail(self.photo, '136x150', crop='center')
