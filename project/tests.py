import datetime
from django.test import TestCase, Client

from django.urls import reverse

from employee.models import Employee
from .models import Project, Issue, Sprint, ProjectTeam
from .forms import EditIssueForm, CreateIssueForm, IssueForm
from django.shortcuts import get_object_or_404


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


class TeamViewTest(LoginRequiredBase):
    def test_team_view_list_view_with_no_team(self):
        project = Project.objects.create(title="Pr1")
        response = self.client.get(reverse('project:team', kwargs={'project_id': project.id}))
        self.assertContains(response, "no team on project", status_code=200)
        self.assertQuerysetEqual(response.context['team_list'], [])

    def test_team_view_list_view_with_one_team(self):
        project = Project.objects.create(title="Pr1")
        team = ProjectTeam.objects.create(project=project, title='title')
        response = self.client.get(reverse('project:team', kwargs={'project_id': project.id}))
        self.assertQuerysetEqual(response.context['team_list'], ['<ProjectTeam: title>'])


class IssueFormTests(LoginRequiredBase):
    def setUp(self):
        super(IssueFormTests, self).setUp()
        self.project = Project.objects.create()
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project, author=self.employee)

    def test_form_is_valid_with_empty_fields(self):
        """
             method should return False if fields are empty
        """
        form = IssueForm()
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_not_null_required_fields(self):
        """
             method should return True if required fields are full
        """
        form_data = {'project': self.project.pk, 'author': self.employee.pk, 'title': 'new issue'}
        form = IssueForm(data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_valid_with_not_null_some_required_fields(self):
        """
             method should return False if some required fields are empty
        """
        form_data = {'project': self.project.pk, 'author': self.employee.pk}
        form = IssueForm(data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_all_fields_are_full(self):
        """
             method should return True if all fields are full right
        """
        form_data = {'root': self.issue.pk, 'project': self.project.pk,
                     'author': self.employee.pk, 'employee': self.employee.pk,
                     'title': 'new issue', 'description': 'description',
                     'status': self.issue.status, 'estimation': 2
        }
        form = IssueForm(data=form_data)
        self.assertEqual(form.is_valid(), True)


class IssueEditViewTests(LoginRequiredBase):
    def setUp(self):
        super(IssueEditViewTests, self).setUp()
        self.client = Client()
        self.project = Project.objects.create()
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project, author=self.employee, title='title')

    def test_issue_edit_view_use_right_template(self):
        """
            method should return OK if it use right template
        """
        response = self.client.post(reverse('project:issue_edit', args=[self.project.pk,
                                                                        self.issue.pk]))
        self.assertTemplateUsed(response, 'project/edit_issue.html')

    def test_issue_edit_view_can_get_object(self):
        """
            method should be True and return title if it can get an object
        """
        issue = get_object_or_404(Issue, pk=self.issue.pk, project=self.project.pk)
        self.assertTrue(isinstance(issue, Issue))
        self.assertEqual(issue.__str__(), issue.title)

    # def test_issue_edit_view_cant_get_object(self):
    #     """
    #         method should return False if it cant get an object
    #     """
    #     try:
    #         issue = get_object_or_404(Issue, pk=0, project=0)
    #     except Issue.DoesNotExist:
    #         raise Http404("Project does not exist")
    #     self.assertTrue(isinstance(issue, Issue), False)


class IssueCreateViewTests(LoginRequiredBase):
    def setUp(self):
        super(IssueCreateViewTests, self).setUp()
        self.client = Client()
        self.project = Project.objects.create()
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project, author=self.employee, title='title')

    def test_issue_create_view_use_right_template(self):
        """
            method should return OK if it use right template
        """
        response = self.client.post(reverse('project:issue_create', args=[self.project.pk]))
        self.assertTemplateUsed(response, 'project/create_issue.html')


class ProjectsListViewTests(LoginRequiredBase):
    def test_projectlist_view_with_no_projects(self):
        response = self.client.get(reverse('project:list'))
        self.assertContains(response, "There is no projects yet.", status_code=200)
        self.assertQuerysetEqual(response.context['project_list'], [])

    def test_projectlist_view_with_projects(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('project:list'))
        self.assertQuerysetEqual(response.context['project_list'],
                                 ['<Project: title>'])


class BacklogViewTests(LoginRequiredBase):
    def test_backlog_view_with_no_issues(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:backlog',
                                           kwargs={'project_id': project.id}))
        self.assertContains(response, "No issues.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_issues(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        employee = Employee.objects.create(role=Employee.DEVELOPER)
        Issue.objects.create(project=project,
                             author=employee, title='title')
        response = self.client.get(reverse('project:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'],
                                 ['<Issue: title>'])

    def test_backlog_view_with_issues_which_belongs_to_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        employee = Employee.objects.create(role=Employee.DEVELOPER)
        team = ProjectTeam.objects.create(project=project, title='title')
        sprint = Sprint.objects.create(title='title', project=project,
                                       team=team)
        Issue.objects.create(project=project, author=employee,
                             title='title', sprint=sprint)
        response = self.client.get(reverse('project:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:backlog',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class SprintsListViewTests(LoginRequiredBase):
    def test_sprints_list_view_with_no_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "No sprints.")
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project, team=team)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'],
                                 ['<Sprint: title>'])

    def test_sprints_list_view_must_not_consist_active_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              team=team, status=Sprint.ACTIVE)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class ProjectViewTests(LoginRequiredBase):
    def setUp(self):
        # Set up data for the whole TestCase
        self.project = Project.objects.create(title='only a test',
                                             description='yes, this is only a test',
                                             start_date=datetime.date(
                                                 2017, 12, 14),
                                             end_date=datetime.date(
                                                 2017, 12, 14))

        # create

    def test_project_create(self):
        response = self.client.get(reverse('project:create'))
        self.assertEqual(response.status_code, 200)

    def check_how_many_objects_are_in_db_now(self):
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
            reverse('project:detail',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_update_valid(self):
        test_project = Project.objects.all()[0]
        form_data = {'title': test_project.title + '123',
                     'description': test_project.description + '123',
                     'start_date': test_project.start_date + datetime.timedelta(
                         days=1),
                     'end_date': test_project.end_date + datetime.timedelta(
                         days=1)}
        form = Project(data=form_data)
        self.assertTrue(form.is_valid())


        # delete

    def test_project_delete_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('project:delete',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_is_really_deleted(self):
        test_project = Project.objects.all()[0]

        response = self.client.get(reverse('workflow:project_delete',
                    kwargs={'pk': test_project.id}))


    # detail

    def test_project_detail_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('project:detail',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)
