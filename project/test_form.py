import datetime
from django.test import TestCase, Client
from django.core.management import call_command

from django.urls import reverse

from employee.models import Employee
from project.forms import ProjectForm
from .models import Project, Issue, Sprint, ProjectTeam
from .forms import IssueForm
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _


class LoginRequiredBase(TestCase):
    def __init__(self, *args, **kwargs):
        super(LoginRequiredBase, self).__init__(*args, **kwargs)
        # self.user_role_init = Employee.DEVELOPER

    def setUp(self):
        self.client = Client()
        self.user = Employee.objects.create_user('john',
                                                 'lennon@thebeatles.com',
                                                 'johnpassword',
                                                 first_name='Miss',
                                                 last_name='Mister',
                                                 is_staff=True)
        self.client.login(username='john', password='johnpassword')
        call_command('loaddata', 'project/fixtures/test.json', verbosity=1)


class IssueFormTests(LoginRequiredBase):
    def setUp(self):
        super(IssueFormTests, self).setUp()
        self.project = Project.objects.create(title='title')
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.user, title='title')
        self.sprint = Sprint.objects.create(title='title', project=self.project)
        self.team = ProjectTeam.objects.create(project=self.project, title='title')
        self.team.employees.add(self.user)

    def test_form_is_not_valid_with_no_sprint_and_status_distinct_new(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.RESOLVED, 'estimation': 2
                     }
        response = self.client.post(reverse('project:issue_edit', self.project.pk,
                                            self.issue.pk), form_data)
        self.assertFormError(response, 'IssueFormForEditing', 'status',
                             'The issue unrelated to sprint has to be NEW')
