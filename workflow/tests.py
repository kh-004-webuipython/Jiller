from django.test import TestCase
from django.urls import reverse

from django.urls import reverse

from .models import Project, Issue, Employee, Sprint, ProjectTeam

class BacklogViewTests(TestCase):
    def test_backlog_view_with_no_issues(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id, ]))
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
                                           args=[project.id+1, ]))
        self.assertEqual(response.status_code, 404)

class SprintsListViewTests(TestCase):
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
from .models import Project


class ProjectTests(TestCase):
    def create_project(self, title='only a test',
                       description='yes, this is only a test',
                       start_date='2017-12-14', end_date='2017-12-14'):
        return Project.objects.create(title=title, description=description,
                                      start_date=start_date, end_date=end_date)

    def test_project_creation(self):
        test_project = self.create_project()
        self.assertTrue(isinstance(test_project, Project))

    # views (uses reverse)

    # def test_project_list_view(self):
    #     w = self.create_project()
    #     url = reverse("workflow.views.ProjectListView")
    #     resp = self.client.get(url)
    #
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn(w.title, resp.content)

    def test_project_create(self):
        response = self.client.get(reverse('workflow:project_create'))
        self.assertEqual(response.status_code, 200)

    def test_project_detail(self):
        test_project = self.create_project()
        response = self.client.get(reverse('workflow:project_detail', kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)
