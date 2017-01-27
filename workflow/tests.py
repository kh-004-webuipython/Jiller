from django.test import TestCase

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
