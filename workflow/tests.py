from django.test import TestCase
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from .models import Sprint, Project, ProjectTeam, Employee, Issue

"""
c = Client()
response = c.post('/login/', {'username': 'admin', 'password': 'qwerty'})
response.status_code
200

assertContains(response, text, ...)
assertTemplateUsed(response, template_name, ...)
assertRedirects(response, expected_url, ...)

"""


def create_project(title='test'):
    return Project.objects.create(title=title)


def create_user(username='testuser', password='12qwaszx',
                role='Product Owner'):
    return Employee.objects.create(username=username, password=password,
                                   role=role)


def create_team(project=1, title='test_team', user='test_user'):
    return ProjectTeam.objects.create(project=project, title=title, user=user)


def create_sprint(title='test_sprint', project=1):
    return Sprint.objects.create(title=title, project_id=project,
                                 team_id=1,
                                 start_date=timezone.now(),
                                 end_date=timezone.now(), order=1,
                                 status='Active')


def create_issue(sprint=1, title='test_issue', author=1):
    return Issue.objects.create(sprint_id=sprint, title=title,
                                author_id=author, project_id=1)


class SprintResponseTests(TestCase):
    def test_workflow_sprint_on_response(self):
        t_sprint = create_sprint()
        url = reverse('workflow:sprint',
                      args=(t_sprint.project_id, t_sprint.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_sprint_response_404(self):
        url = reverse('workflow:sprint', args=(1, 1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_workflow_issue_on_response(self):
        create_sprint()
        create_project()
        t_issue = create_issue()
        url = reverse('workflow:issue',
                      args=(t_issue.project_id, t_issue.id))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_issue_response_404(self):
        url = reverse('workflow:issue',
                      args=(1, 1))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_html_what_is_using_on_issue(self):
        create_sprint()
        create_project()
        create_issue()
        url = reverse('workflow:issue', args=(1, 1))
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'workflow/issue.html')

    """
    def test_workflow_sprint_on_201_response(self):
        create_project()
        create_issue()
        url = reverse('workflow:sprint_create', args=(1))
        data = {'title':1, 'project_id':1, 'team_id':1,
                'start_date':timezone.now(), 'end_date':timezone.now(),
                'order':1, 'status':'Active'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)
        """


