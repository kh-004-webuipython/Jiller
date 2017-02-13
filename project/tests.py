import datetime
from django.test import TestCase, Client
from django.core.management import call_command

from django.urls import reverse

from employee.models import Employee
from project.forms import ProjectForm
from .models import Project, Issue, Sprint, ProjectTeam, ProjectNote
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


class TeamViewTest(LoginRequiredBase):
    def test_team_view_list_view_with_no_team(self):
        project = Project.objects.create(title="Pr1")
        response = self.client.get(
            reverse('project:team', kwargs={'project_id': project.id}))
        self.assertContains(response, "no team on project", status_code=200)
        self.assertQuerysetEqual(response.context['team_list'], [])

    def test_team_view_list_view_with_one_team(self):
        project = Project.objects.create(title="Pr1")
        team = ProjectTeam.objects.create(project=project, title='title')
        response = self.client.get(
            reverse('project:team', kwargs={'project_id': project.id}))
        self.assertQuerysetEqual(response.context['team_list'],
                                 ['<ProjectTeam: title>'])


class IssueFormTests(LoginRequiredBase):
    def setUp(self):
        super(IssueFormTests, self).setUp()
        self.project = Project.objects.create()
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee)
        self.sprint = Sprint.objects.create(title='title',
                                            project=self.project)
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')

    def test_form_is_valid_with_empty_fields(self):
        """
             method should return False if fields are empty
        """
        form = IssueForm(project=self.project)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_not_null_required_fields(self):
        """
             method should return True if required fields are full
        """
        form_data = {'title': 'new issue'}
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_valid_with_not_null_some_required_fields(self):
        """
             method should return False if some required fields are empty
        """
        form_data = {}
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_all_fields_are_full(self):
        """
             method should return True if all fields are full right
        """
        form_data = {'root': self.issue.pk, 'employee': self.employee.pk,
                     'title': 'new issue', 'description': 'description',
                     'status': self.issue.status, 'estimation': 2
                     }
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_not_valid_with_no_sprint_and_status_distinct_new(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.RESOLVED, 'estimation': 2
                     }
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_not_valid_with_sprint_and_status_new(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.NEW, 'estimation': 2,
                     'sprint': self.sprint
                     }
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_not_valid_with_sprint_and_no_estimation(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.IN_PROGRESS, 'sprint': self.sprint
                     }
        form = IssueForm(project=self.project, data=form_data)
        self.assertEqual(form.is_valid(), False)


class IssueEditViewTests(LoginRequiredBase):
    def setUp(self):
        super(IssueEditViewTests, self).setUp()
        self.client = Client()
        self.project = Project.objects.create()
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title')
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')
        self.team.employees.add(self.user)

    def test_issue_edit_view_use_right_template(self):
        """
            method should return OK if it use right template
        """
        response = self.client.post(
            reverse('project:issue_edit', args=[self.project.pk,
                                                self.issue.pk]))
        self.assertTemplateUsed(response, 'project/issue_edit.html')

    def test_issue_edit_view_can_get_object(self):
        """
            method should be True and return title if it can get an object
        """
        issue = get_object_or_404(Issue, pk=self.issue.pk,
                                  project=self.project.pk)
        self.assertTrue(isinstance(issue, Issue))
        self.assertEqual(issue.__str__(), issue.title)

    def test_issue_edit_view_can_get_object(self):
        """
            method should be True and return title if it can get an object
        """
        issue = get_object_or_404(Issue, pk=self.issue.pk,
                                  project=self.project.pk)
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
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title')

    def test_issue_create_view_use_right_template(self):
        """
            method should return OK if it use right template
        """
        response = self.client.post(
            reverse('project:issue_create', args=[self.project.pk]))
        self.assertTemplateUsed(response, 'project/issue_create.html')


class ProjectsListViewTests(LoginRequiredBase):
    def test_projectlist_view_with_no_projects(self):
        response = self.client.get(reverse('project:list'))
        self.assertContains(response, "There is no projects yet.",
                            status_code=200)
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
        employee = Employee.objects.create()
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
        employee = Employee.objects.create()
        team = ProjectTeam.objects.create(project=project, title='title')
        sprint = Sprint.objects.create(title='title', project=project)
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
        self.assertEqual(response.status_code, 200)

    def test_sprints_list_view_with_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        Sprint.objects.create(title='title', project=project)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "title", status_code=200)

    def test_sprints_list_view_must_not_consist_active_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              status=Sprint.ACTIVE)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "", status_code=200)

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
        super(ProjectViewTests, self).setUp()
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

    def test_check_how_many_objects_are_in_db_now(self):
        all_projects_in_database = Project.objects.all()
        self.assertEquals(all_projects_in_database.count(), 1)

    def test_check_all_project_attributes(self):
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
        response = self.client.post(
            reverse('project:update',
                    kwargs={'project_id': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_update_valid(self):
        test_project = Project.objects.all()[0]
        date = datetime.datetime.strptime('24052010', "%d%m%Y").date()
        form_data = {'title': test_project.title + '123',
                     'description': test_project.description + '123',
                     'start_date': date + datetime.timedelta(
                         days=1),
                     'end_date': date + datetime.timedelta(
                         days=2)}
        response = self.client.post(
            reverse('project:update',
                    kwargs={'project_id': test_project.id}), data=form_data)
        url_detail = reverse('project:detail',
                             kwargs={'project_id': test_project.id})
        self.assertRedirects(response, url_detail, status_code=302,
                             target_status_code=200)
        test_project = Project.objects.all()[0]
        self.assertEquals(test_project.title, 'only a test123')
        self.assertEquals(test_project.title, 'only a test123')
        self.assertEquals(test_project.description,
                          'yes, this is only a test123')
        self.assertEquals(test_project.start_date,
                          date + datetime.timedelta(
                              days=1))
        self.assertEquals(test_project.end_date,
                          date + datetime.timedelta(
                              days=2))

    def test_incorrect_date(self):
        test_project = Project.objects.all()[0]
        date = datetime.datetime.strptime('24052010', "%d%m%Y").date()
        form_data = {'start_date': date + datetime.timedelta(
            days=5),
                     'end_date': date + datetime.timedelta(
                         days=2)}
        response = self.client.post(
            reverse('project:update',
                    kwargs={'project_id': test_project.id}), data=form_data)
        test_project = Project.objects.all()[0]
        self.assertNotEquals(test_project.start_date,
                             date + datetime.timedelta(
                                 days=5))

        # delete

    def test_project_delete_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('project:delete',
                    kwargs={'project_id': test_project.id}))
        self.assertEqual(response.status_code, 200)

    def test_project_is_really_deleted(self):
        test_project = Project.objects.all()[0]
        response = self.client.post(
            reverse('project:delete',
                    kwargs={'project_id': test_project.id}))
        url_detail = reverse('project:list')
        self.assertRedirects(response, url_detail, status_code=302,
                             target_status_code=200)
        test_project = Project.objects.all()[0]
        self.assertEquals(test_project.is_active, False)

    # detail

    def test_project_detail_page(self):
        test_project = self.project
        response = self.client.get(
            reverse('project:detail',
                    kwargs={'project_id': test_project.id}))
        self.assertEqual(response.status_code, 200)


class SprintResponseTests(LoginRequiredBase):
    def test_project_sprint_response_200(self):
        project = Project.objects.create(title='Test Project')
        ProjectTeam.objects.create(project=project, title='Test Team')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status='new')
        url = reverse('project:sprint_detail',
                      kwargs={'project_id': sprint.project_id,
                              'sprint_id': sprint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_sprint_response_404(self):
        url = reverse('project:sprint_detail', kwargs={'project_id': 100,
                                                       'sprint_id': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_project_sprint_create(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status='new')
        url = reverse('project:sprint_create',
                      kwargs={'project_id': sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        inst_count = len(Sprint.objects.all())
        self.assertEqual(Sprint.objects.get(pk=1).status, 'new')
        start_date = datetime.datetime.now().strftime("%Y-%m-%d")
        end_date = datetime.datetime.now() + datetime.timedelta(days=14)
        end_date = end_date.strftime("%Y-%m-%d")
        data = {'title': "It's a New Sprint", 'project': project.id,
                "start_date": start_date, "end_date": end_date,
                'status': 'new'}
        response = self.client.post(url, data)
        new_sprint = Sprint.objects.get(pk=2)
        self.assertEquals(new_sprint.start_date.strftime("%Y-%m-%d"),
                          start_date)
        # self.assertEquals(new_sprint.end_date.strftime("%Y-%m-%d"), end_date)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Sprint.objects.all()), inst_count + 1)

        # will not pass, cuz there no such functionality
        """
        self.assertEqual(Sprint.objects.get(pk=1).order, 1)
        self.assertEqual(Sprint.objects.get(pk=2).order, 2)
        self.assertEqual(Sprint.objects.get(pk=2).status, 'new')
        """


class IssueResponseTests(LoginRequiredBase):
    def test_project_issue_response_200(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        Sprint.objects.create(title='T_sprint', project_id=project.id,
                              status='new')
        issue = Issue.objects.create(sprint_id=1, title='T_issue', author_id=1,
                                     project_id=1,
                                     status='new')
        url = reverse('project:issue_detail',
                      kwargs={'project_id': issue.project_id,
                              'issue_id': issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_issue_response_404(self):
        url = reverse('project:issue_detail',
                      kwargs={'project_id': 100, 'issue_id': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_using_html_on_issue(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        Sprint.objects.create(title='T_sprint', project_id=project.id,
                              status='new')
        issue = Issue.objects.create(sprint_id=1, title='T_issue', author_id=1,
                                     project_id=1,
                                     status='new')
        url = reverse('project:issue_detail',
                      kwargs={'project_id': issue.project_id,
                              'issue_id': issue.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'project/issue_detail.html')


class ActiveSprintTests(LoginRequiredBase):
    def test_project_sprint_active_response_200(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status='active')
        self.assertEqual(Sprint.objects.get(pk=1).status, 'active')
        url = reverse('project:sprint_active',
                      kwargs={'project_id': sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_project_sprint_active_response_404(self):
        Project.objects.create(title='Test Project')
        url = reverse('project:sprint_active', kwargs={'pk': 100})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_all_unfinished_issues_after_sprint_ends_move_to_backlog(self):
        number_of_issues = 10
        project = Project.objects.create(title='Test Project')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status='active')
        for i in range(number_of_issues):
            Issue.objects.create(title='Test Issue {}'.format(i),
                                 project=project, order=Issue.MEDIUM,
                                 author=self.user)

        issue_sprints = []
        issue_resolved = []
        issue_closed = []
        issue_in_progress = []
        issue_new = []
        for i, issue in enumerate(
                Issue.objects.all().order_by('order')[number_of_issues / 2:]):
            issue.sprint = sprint
            if not i % 3:
                issue.status = Issue.RESOLVED
                issue_resolved.append(issue)
            elif not i % 2 and i % 4:
                issue.status = Issue.CLOSED
                issue_closed.append(issue)
            elif not i % 4:
                issue.status = Issue.IN_PROGRESS
                issue_in_progress.append(issue)
            else:
                issue_new.append(issue)
            issue.save()
            issue_sprints.append(issue)

        sprint.status = Sprint.FINISHED
        sprint.save()
        sprint.refresh_from_db()
        for issue in issue_sprints:
            issue.refresh_from_db()
        highest_backlog_issues = Issue.objects.filter(project=project.id,
                                                      sprint=None).order_by(
            'order')[
                                 :2 + len(issue_new) + len(issue_in_progress)]
        print(highest_backlog_issues)
        for issue in issue_closed:
            self.assertTrue(issue.sprint == sprint)
            self.assertTrue(issue.status == Issue.CLOSED)
        for issue in issue_resolved:
            self.assertTrue(issue.sprint == sprint)
            self.assertTrue(issue.status == Issue.RESOLVED)
        for issue in issue_in_progress:
            self.assertIsNone(issue.sprint)
            self.assertTrue(issue.status == Issue.NEW)
            self.assertTrue(issue in highest_backlog_issues)
        for issue in issue_new:
            self.assertIsNone(issue.sprint)
            self.assertTrue(issue.status == Issue.NEW)
            self.assertTrue(issue in highest_backlog_issues)


class SprintDashboard(LoginRequiredBase):
    def setUp(self):
        super(SprintDashboard, self).setUp()
        self.project = Project.objects.create(title='pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status='active')
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status='new', sprint=self.sprint)

    def test_project_issue_push_right(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        Sprint.objects.create(title='T_sprint', project_id=project.id, status='active')
        iss_new = Issue.objects.create(sprint_id=1, title='T_issue',
                                       author_id=1, project_id=1,
                                       status='new')
        self.assertEqual(iss_new.status, 'new')

        url = reverse('project:issue_push',
                      kwargs={'project_id': iss_new.project_id,
                              'issue_id': iss_new.id, 'slug': 'right'})
        self.client.get(url)

        changed_issue = Issue.objects.get(pk=iss_new.id)
        self.assertEqual(changed_issue.status, 'in progress')
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_new.id)
        self.assertEqual(changed_issue.status, 'resolved')

        iss_prog = Issue.objects.create(sprint_id=1, title='T_issue',
                                        author_id=1, project_id=1,
                                        status='in progress')
        url = reverse('project:issue_push',
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

    def test_project_issue_push_left(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        Sprint.objects.create(title='T_sprint', project_id=project.id, status='active')
        iss_res = Issue.objects.create(sprint_id=1, title='T_issue',
                                       author_id=1, project_id=1,
                                       status='resolved')
        self.assertEqual(iss_res.status, 'resolved')
        url = reverse('project:issue_push',
                      kwargs={'project_id': iss_res.project_id,
                              'issue_id': iss_res.id, 'slug': 'left'})
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_res.id)
        self.assertEqual(changed_issue.status, 'in progress')
        self.client.get(url)
        changed_issue = Issue.objects.get(pk=iss_res.id)
        self.assertEqual(changed_issue.status, 'new')

        iss_prog = Issue.objects.create(sprint_id=1, title='T_issue',
                                        author_id=1, project_id=1,
                                        status='in progress')
        url = reverse('project:issue_push',
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


class WorkloadManagerTest(LoginRequiredBase):
    def setUp(self):
        super(WorkloadManagerTest, self).setUp()
        self.project = Project.objects.create()
        self.team = ProjectTeam.objects.create(project=self.project, title='title')
        self.team.employees.add(self.user)

    def test_workload_view_with_no_sprint(self):
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id}))
        self.assertEqual(response.status_code, 404)

    def test_workload_view_with_empty_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,
                                       start_date=datetime.date(2017, 12, 14),
                                       end_date=datetime.date(2017, 12, 21),
                                       status=Sprint.ACTIVE, )
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id}))
        self.assertContains(response, "No items.", status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])

    def test_workload_view_with_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,
                                       start_date=datetime.date(2017, 12, 14),
                                       end_date=datetime.date(2017, 12, 21),
                                       status=Sprint.ACTIVE, )
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.user, sprint=sprint,
                                          employee=self.user)
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={'project_id': self.project.id}))
        self.assertContains(response, self.user.username, status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])

    def test_project_issue_push_responses(self):
        response = self.client.get(reverse('project:issue_push'))
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        url = reverse('project:issue_push')
        data = {'table': 'in progress', 'id': 1}
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status, 'new')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status,
                         'in progress')

        data = {'table': 'resolved', 'id': 1}
        self.client.post(url, data)
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status,
                         'resolved')

        url = reverse('project:issue_push')
        data = {'table': 'new', 'id': 2}
        response = self.client.post(url, data)
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        sprint2 = Sprint.objects.create(project=self.project,
                                        status='finished')
        Issue.objects.create(project=self.project,
                             author=self.employee, title='title',
                             status='new', sprint=sprint2)
        url = reverse('project:issue_push')
        data = {'table': 'resolved', 'id': 2}
        response = self.client.post(url, data)
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)


class ProjectNotes(LoginRequiredBase):
    def setUp(self):
        super(ProjectNotes, self).setUp()
        self.project = Project.objects.create(title='pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status='active')
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status='new', sprint=self.sprint)
        self.note = ProjectNote.objects.create(project=self.project,
                                               title='TESTS',
                                               content="some text in Notes")

    def test_notes_get_responses(self):
        response = self.client.get(
            reverse('project:note', kwargs={'project_id': self.project.id}))
        self.assertContains(response, "some text in Notes",
                            status_code=200)

        response = self.client.get(
            reverse('project:note', kwargs={'project_id': 2}))
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

    def test_notes_post_responses(self):
        url = reverse('project:note', kwargs={'project_id': self.project.id})
        data = {'id': 1, 'title': 'title', 'content': 'SOME TEXT#'}
        self.client.post(url, data)
        self.assertEqual(ProjectNote.objects.get(pk=1).content, 'SOME TEXT#')

        data = {'id': 2, 'title': 'title', 'content': 'SOME TEXT'}
        response = self.client.post(url, data)
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        self.assertEqual(len(ProjectNote.objects.all()), 1)
        data = {'id': 'undefined', 'title': 'title', 'content': 'SOME TEXT'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ProjectNote.objects.all()), 2)


""" TODO: need to discuss!
    def test_notes_delete_responses(self):
        url = reverse('project:note', kwargs={'project_id': self.project.id})
        data = {'id': 1}
        self.assertEqual(len(ProjectNote.objects.all()), 1)
        response = self.client.delete(url, data)
        print self.note.id
        print ProjectNote.objects.all(),ProjectNote.objects.get(pk=1)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ProjectNote.objects.all()), 0)
"""
