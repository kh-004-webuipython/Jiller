from django.test import TestCase, Client

from django.urls import reverse
from django.utils import timezone

from .models import Project, Issue, Employee, Sprint, ProjectTeam


class LoginRequiredBase(TestCase):
    def __init__(self, *args, **kwargs):
        super(LoginRequiredBase, self).__init__(*args, **kwargs)
        self.user_role_init = Employee.DEVELOPER

    def setUp(self):
        self.client = Client()
        self.user = Employee.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword', first_name='Miss',
                                                 last_name='Mister', role=self.user_role_init)
        self.client.login(username='john', password='johnpassword')

class ProjectsListViewTests(LoginRequiredBase):
    def test_projectlist_view_with_no_projects(self):
        response = self.client.get(reverse('workflow:projects'))
        self.assertContains(response, "There is no projects yet.", status_code=200)
        self.assertQuerysetEqual(response.context['project_list'], [])

    def test_projectlist_view_with_projects(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:projects'))
        self.assertQuerysetEqual(response.context['project_list'],
                                 ['<Project: title>'])

class ProfileViewTests(LoginRequiredBase):
    def test_profile_view_with_correct_user(self):
        response = self.client.get(reverse('workflow:profile'))
        self.assertContains(response, 'Miss', status_code=200)

    def test_profile_view_with_incorrect_user(self):
        self.user = Employee.objects.create_user('mark', 'webber@redbull.com', 'markpassword', first_name='Kiss',
                                                 last_name='Dismiss', role=self.user_role_init)
        response = self.client.get(reverse('workflow:profile'))
        self.assertNotContains(response, 'Kiss')


class BacklogViewTests(LoginRequiredBase):
    def test_backlog_view_with_no_issues(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           kwargs={'project_id':project.id}))
        self.assertContains(response, "No issues.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_issues(self):
        project = Project.objects.create(title='title')
        employee = Employee.objects.create(role=Employee.DEVELOPER)
        Issue.objects.create(project=project,
                             author=employee, title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'],
                                 ['<Issue: title>'])

    def test_backlog_view_with_issues_which_belongs_to_sprint(self):
        project = Project.objects.create(title='title')
        employee = Employee.objects.create(role=Employee.DEVELOPER)
        team = ProjectTeam.objects.create(project=project, title='title')
        sprint = Sprint.objects.create(title='title', project=project,
                                       team=team)
        Issue.objects.create(project=project, author=employee,
                             title='title', sprint=sprint)
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class SprintsListViewTests(LoginRequiredBase):
    def test_sprints_list_view_with_no_sprint(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "No sprints.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_sprint(self):
        project = Project.objects.create(title='title')
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project, team=team)
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'],
                                 ['<Sprint: title>'])

    def test_sprints_list_view_must_not_consist_active_sprint(self):
        project = Project.objects.create(title='title')
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              team=team, status=Sprint.ACTIVE)
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)
