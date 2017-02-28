from project.models import Sprint, Issue
from employee.models import Employee
from django.http import HttpResponse

from django import forms
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from general.tasks import send_assign_email_task
from employee.models import IssueLog
from general.forms import FormControlMixin
from project.models import Project, Sprint, Issue, ProjectTeam, IssueComment, \
    ProjectNote
from django.db.models import Q


def user_variator(self, user, project):
    if user.groups.all():
        if user.groups.filter(id=3):
            del self.fields['type']
            del self.fields['root']

        if user.groups.filter(pk__in=[1, ]):
            del self.fields['sprint']
