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


class WorkloadManagerTest(LoginRequiredBase):
    def setUp(self):
        super(WorkloadManagerTest, self).setUp()
        self.project = Project.objects.create()
        self.team = ProjectTeam.objects.create(project=self.project, title='title')
        self.team.employees.add(self.user)

    def test_workload_view_with_no_sprint(self):
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id,
                                                   'sprint_status': Sprint.ACTIVE}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/404.html')

    def test_workload_view_with_empty_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,
                                       start_date=datetime.date(2017, 12, 14),
                                       end_date=datetime.date(2017, 12, 21),
                                       status=Sprint.ACTIVE)
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id,
                                                   'sprint_status': Sprint.ACTIVE}))
        self.assertContains(response, "No items.", status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])

    def test_workload_view_with_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,
                                       start_date=datetime.date(2017, 12, 14),
                                       end_date=datetime.date(2017, 12, 21),
                                       status=Sprint.ACTIVE)
        Issue.objects.create(project=self.project, author=self.user,
                             sprint=sprint, employee=self.user)
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id,
                                                   'sprint_status': Sprint.ACTIVE}))
        self.assertContains(response, self.user.username, status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])
