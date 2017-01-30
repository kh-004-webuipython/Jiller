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
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('workflow:backlog',
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
        response = self.client.get(reverse('workflow:backlog',
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
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('workflow:backlog',
                                           args=[project.id + 1, ]))
        self.assertEqual(response.status_code, 404)


class SprintsListViewTests(LoginRequiredBase):
    def test_sprints_list_view_with_no_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('workflow:sprints_list',
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
        response = self.client.get(reverse('workflow:sprints_list',
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
        response = self.client.get(reverse('workflow:sprints_list',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['sprints'], [])

    def test_sprints_list_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('workflow:sprints_list',
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
        response = self.client.get(reverse('workflow:project_create'))
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
            reverse('workflow:project_detail',
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
            reverse('workflow:project_delete',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_is_really_deleted(self):
        test_project = Project.objects.all()[0]

        # response = self.client.get(reverse('workflow:project_delete',
        #             kwargs={'pk': test_project.id}))


    # detail

    def test_project_detail_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('workflow:project_detail',
                    kwargs={'pk': test_project.id}))
        self.assertEqual(response.status_code, 200)

######################################################################TODO:
def create_project(title='test_project'):
    return Project.objects.create(title=title)


def create_user(username='test_user', password='test_user',
                role='developer'):
    return Employee.objects.create(username=username, password=password,
                                   role=role)


def create_team(project=1, title='test_team'):
    return ProjectTeam.objects.create(project=project, title=title)


def create_sprint(title='test_sprint', project=1, status='new'):
    return Sprint.objects.create(title=title, project_id=project,
                                 team_id=1,
                                 start_date=timezone.now(),
                                 end_date=timezone.now(), order=1,
                                 status=status)


def create_issue(sprint=1, title='test_issue', author=1, status='new'):
    return Issue.objects.create(sprint_id=sprint, title=title,
                                author_id=author, project_id=1, status=status)


class SprintResponseTests(LoginRequiredBase):
    def test_workflow_sprint_response_200(self):
        create_project()
        sprint = create_sprint()
        url = reverse('workflow:sprint',
                      kwargs={'project_id': sprint.project_id,
                              'sprint_id': sprint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_workflow_sprint_response_404(self):
        url = reverse('workflow:sprint', kwargs={'project_id': 100,
                                                 'sprint_id': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_workflow_sprint_create(self):
        project = create_project()
        team = create_team(project)
        sprint = create_sprint()
        url = reverse('workflow:sprint_create',
                      kwargs={'pk': sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        inst_count = len(Sprint.objects.all())

        # will not pass, cuz there no such functionality
        self.assertEqual(Sprint.objects.get(pk=1).status, 'new')
        self.assertEqual(Sprint.objects.get(pk=1).order, 1)
        start_date = timezone.now()
        end_date = timezone.now() + timezone.timedelta(days=14)
        data = {'title': "It's a New Sprint", 'project': project.id,
                'team': team.id, }
        response = self.client.post(url, data, follow=True)
        print response.redirect_chain
        print Sprint.objects.get(pk=2)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Sprint.objects.all()), inst_count + 1)

        """
        self.assertEqual(Sprint.objects.get(pk=2).order, 2)
        self.assertEqual(Sprint.objects.get(pk=2).status, 'new')
        """


class IssueResponseTests(LoginRequiredBase):
    def test_workflow_issue_response_200(self):
        create_project()
        create_sprint()
        issue = create_issue()
        url = reverse('workflow:issue',
                      kwargs={'project_id': issue.project_id,
                              'issue_id': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_workflow_issue_response_404(self):
        url = reverse('workflow:issue',
                      kwargs={'project_id': 100, 'issue_id': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_using_html_on_issue(self):
        create_sprint()
        create_project()
        issue = create_issue()
        url = reverse('workflow:issue', kwargs={'project_id': issue.project_id,
                                                'issue_id': issue.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'workflow/issue.html')


class ActiveSprintTests(LoginRequiredBase):
    def test_workflow_active_sprint_response_200(self):
        create_project()
        sprint = create_sprint(status='active')
        self.assertEqual(Sprint.objects.get(pk=1).status, 'active')
        url = reverse('workflow:active_sprint',
                      kwargs={'pk': sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_workflow_sprint_response_404(self):
        create_project()
        url = reverse('workflow:active_sprint', kwargs={'pk': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class SprintDashboard(LoginRequiredBase):
    def test_workflow_issue_push_response_302(self):
        create_project()
        sprint = create_sprint(status='active')
        iss_new = create_issue()
        iss_res = create_issue(status='resolved')
        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_new.project_id,
                              'issue_id': iss_new.id, 'slug': 'right'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url_redirect = reverse('workflow:active_sprint',
                               kwargs={'pk': sprint.project_id})
        self.assertEqual(response['Location'], url_redirect)

        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_res.project_id,
                              'issue_id': iss_res.id, 'slug': 'left'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        url_redirect = reverse('workflow:active_sprint',
                               kwargs={'pk': sprint.project_id})
        self.assertEqual(response['Location'], url_redirect)

    def test_workflow_issue_push_right(self):
        create_project()
        create_sprint(status='active')
        iss_new = create_issue(status='new')
        self.assertEqual(iss_new.status, 'new')
        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_new.project_id,
                              'issue_id': iss_new.id, 'slug': 'right'})
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_new.id)
        self.assertEqual(changed_issue.status, 'in progress')
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_new.id)
        self.assertEqual(changed_issue.status, 'resolved')

        iss_prog = create_issue(status='in progress')
        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_prog.project_id,
                              'issue_id': iss_prog.id, 'slug': 'right'})
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_prog.id)
        self.assertEqual(changed_issue.status, 'resolved')

        # check incorrect push to right
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_prog.id)
        self.assertEqual(changed_issue.status, 'resolved')
        self.assertEqual(len(Issue.objects.all()), 2)

    def test_workflow_issue_push_left(self):
        create_project()
        create_sprint(status='active')
        iss_res = create_issue(status='resolved')
        self.assertEqual(iss_res.status, 'resolved')
        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_res.project_id,
                              'issue_id': iss_res.id, 'slug': 'left'})
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_res.id)
        self.assertEqual(changed_issue.status, 'in progress')
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_res.id)
        self.assertEqual(changed_issue.status, 'new')

        iss_prog = create_issue(status='in progress')
        url = reverse('workflow:issue_push',
                      kwargs={'project_id': iss_prog.project_id,
                              'issue_id': iss_prog.id, 'slug': 'left'})
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_prog.id)
        self.assertEqual(changed_issue.status, 'new')

        #  check incorrect push to left
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_prog.id)
        self.assertEqual(changed_issue.status, 'new')
        self.assertEqual(len(Issue.objects.all()), 2)
