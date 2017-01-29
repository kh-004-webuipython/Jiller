import datetime
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
        self.user = Employee.objects.create_user('john',
                                                 'lennon@thebeatles.com',
                                                 'johnpassword',
                                                 first_name='Miss',
                                                 last_name='Mister',
                                                 role=self.user_role_init)
        self.client.login(username='john', password='johnpassword')


class BacklogViewTests(LoginRequiredBase):
    def test_backlog_view_with_no_issues(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        response = self.client.get(reverse('workflow:backlog',
                                           kwargs={'project_id': project.id}))
        self.assertContains(response, "No issues.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_issues(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        employee = Employee.objects.create(role=Employee.DEVELOPER)
        Issue.objects.create(project=project,
                             author=employee, title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'],
                                 ['<Issue: title>'])

    def test_backlog_view_with_issues_which_belongs_to_sprint(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
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
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class SprintsListViewTests(LoginRequiredBase):
    def test_sprints_list_view_with_no_sprint(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "No sprints.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_sprint(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project, team=team)
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'],
                                 ['<Sprint: title>'])

    def test_sprints_list_view_must_not_consist_active_sprint(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              team=team, status=Sprint.ACTIVE)
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',start_date=datetime.date(
                                                 2017, 12, 14))
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class ProjectViewTests(LoginRequiredBase):
    @classmethod
    def setUpTestData(cls):
        # Set up data for the whole TestCase
        cls.project = Project.objects.create(title='only a test',
                                             description='yes, this is only a test',
                                             start_date=datetime.date(
                                                 2017, 12, 14),
                                             end_date=datetime.date(
                                                 2017, 12, 14))

        # create

    def test_project_create(self):
        response = self.client.get(reverse('workflow:project_create'))
        self.assertEqual(response.status_code, 200)

    def check_how_many_oprojects_is_in_db_now(self):
        all_projects_in_database = Project.objects.all()
        self.assertEquals(all_projects_in_database.count(), 1)

    def check_all_project_attributes(self):
        only_project_in_database = Project.objects.all()[0]
        self.assertEquals(only_project_in_database, self.project)
        self.assertEquals(only_project_in_database.title,
                          'only a test')
        self.assertEquals(only_project_in_database.description,
                          'yes, this is only a test')
        self.assertEquals(only_project_in_database.start_date,
                          self.project.start_date)
        self.assertEquals(only_project_in_database.end_date,
                          self.project.end_date)

        # update

    def test_project_update_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('workflow:project_detail',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_update(self):
        test_project = self.project


        # delete

    def test_project_delete_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('workflow:project_delete',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

        # detail

    def test_project_detail_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('workflow:project_detail',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)
