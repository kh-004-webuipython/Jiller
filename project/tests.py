import datetime
from django.test import TestCase, Client
from django.core.management import call_command
from django.http import Http404
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

from employee.models import Employee
from .models import Project, Issue, Sprint, ProjectTeam, ProjectNote
from .forms import IssueForm



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
    def setUp(self):
        super(TeamViewTest, self).setUp()
        self.project = Project.objects.create(title="Pr1")
        self.sprint = Sprint.objects.create(project=self.project,
                                            status='active', duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status='new', sprint=self.sprint, estimation=1)

    # it's a new test, don't delete
    def test_on_create_2nd_team_on_project_at_time(self):
        team = ProjectTeam.objects.create(project=self.project, title='title')
        self.assertEqual(
            ProjectTeam.objects.filter(project_id=self.project.id).count(), 1)
        try:
            ProjectTeam.objects.create(project=self.project)
        except ValidationError:
            self.assertEqual(
                ProjectTeam.objects.filter(project_id=self.project.id).count(),
                1)

    def test_team_view_list_view_with_no_team(self):
        """
             method should return 404 if no team on project
        """
        try:
            response = self.client.post(
                reverse('project:team',
                        kwargs={'project_id': self.project.pk}))
        except ProjectTeam.DoesNotExist:
            raise Http404("no team on project")
        self.assertTemplateUsed(response, 'general/404.html')

    def test_team_view_list_view_with_one_team(self):
        """
             method should return True if template with given name was used
             and there is one team in ProjectTeam
        """
        project = Project.objects.create(title="Pr1")
        team = ProjectTeam.objects.create(project=project, title='title')
        response = self.client.post(
            reverse('project:team', kwargs={'project_id': project.id}))
        self.assertTemplateUsed(template_name='team.html')
        self.assertTrue(isinstance(team, ProjectTeam), True)
        self.assertIsNotNone(response.context)


class IssueFormTests(LoginRequiredBase):
    def setUp(self):
        super(IssueFormTests, self).setUp()
        self.project = Project.objects.create(title='title')
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, estimation=1)
        self.sprint = Sprint.objects.create(title='title',
                                            project=self.project, duration=10)
        self.new_group, self.created = Group.objects.get_or_create(name='developer')
        self.employee.groups.add(1)
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')
        self.team.employees.add(self.user)

    def test_form_is_valid_with_empty_fields(self):
        """
             method should return False if fields are empty
        """
        form = IssueForm(project=self.project, user=self.user)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_not_null_required_fields(self):
        """
             method should return True if required fields are full
        """
        form_data = {'project': self.project, 'title': 'new issue', 'estimation': 1,
                     'author': self.employee, 'status': Issue.NEW,
                     'type': Issue.TASK, 'order': Issue.HIGH}

        form = IssueForm(project=self.project, data=form_data,
                         user=self.employee)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_valid_with_not_null_some_required_fields(self):
        """
             method should return False if some required fields are empty
        """
        form_data = {}
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_all_fields_are_full(self):
        """
             method should return True if all fields are full right
        """
        form_data = {'project': self.project, 'title': 'new issue', 'estimation': 1,
                     'author': self.employee, 'status': Issue.RESOLVED,
                     'type': Issue.TASK, 'order': Issue.HIGH, 'description': 'description', 'sprint': 1}

        form = IssueForm(project=self.project, data=form_data,
                         user=self.employee)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_not_valid_with_no_sprint_and_status_distinct_new(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.RESOLVED, 'estimation': 2
                     }
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_not_valid_with_sprint_and_status_new(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.NEW, 'estimation': 2,
                     'sprint': self.sprint
                     }
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_not_valid_with_sprint_and_no_estimation(self):
        form_data = {'root': self.issue, 'employee': self.user,
                     'title': 'new issue', 'description': 'description',
                     'status': Issue.IN_PROGRESS, 'sprint': self.sprint
                     }
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), False)

    def test_form_is_valid_with_po_make_user_story(self):
        self.employee.groups.remove()
        self.employee.groups.add(3)
        form_data = {'project': self.project, 'title': 'new issue', 'estimation': 1,
                     'author': self.employee, 'status': Issue.NEW,
                     'type': Issue.USER_STORY, 'order': Issue.HIGH,
                     'description': 'description', 'sprint': 1}
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), True)

    def test_form_is_valid_with_dev_make_task(self):
        form_data = {'project': self.project, 'title': 'new issue', 'estimation': 1,
                     'author': self.employee, 'status': Issue.NEW,
                     'type': Issue.TASK, 'order': Issue.HIGH,
                     'description': 'description', 'sprint': 1}
        form = IssueForm(project=self.project, data=form_data,
                         user=self.user)
        self.assertEqual(form.is_valid(), True)


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
        Issue.objects.create(project=project, estimation=1,
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
        sprint = Sprint.objects.create(title='title', project=project,
                                       duration=10)
        Issue.objects.create(project=project, author=employee,
                             title='title', sprint=sprint, estimation=1)
        response = self.client.get(reverse('project:backlog',
                                           args=[project.id, ]))
        self.assertQuerysetEqual(response.context['issues'], [])

    def test_backlog_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:backlog',
                                           args=[project.id + 1, ]))
        self.assertTemplateUsed(response, 'general/404.html')


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
        Sprint.objects.create(title='title', project=project, duration=10,
                              start_date=datetime.date(2017, 2, 2))
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "title", status_code=200)

    def test_sprints_list_view_must_not_consist_active_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              start_date=datetime.date(2017, 2, 2),
                              status=Sprint.ACTIVE, duration=10)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "", status_code=200)

    def test_sprints_list_view_must_not_consist_new_sprint(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        team = ProjectTeam.objects.create(project=project, title='title')
        Sprint.objects.create(title='title', project=project,
                              start_date=datetime.date(2017, 2, 2),
                              status=Sprint.NEW, duration=10)
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id, ]))
        self.assertContains(response, "", status_code=200)

    def test_sprints_list_view_with_nonexistent_project(self):
        project = Project.objects.create(title='title',
                                         start_date=datetime.date(
                                             2017, 12, 14))
        response = self.client.get(reverse('project:sprints_list',
                                           args=[project.id + 1, ]))
        self.assertTemplateUsed(response, 'general/404.html')


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
    def setUp(self):
        super(SprintResponseTests, self).setUp()
        self.project = Project.objects.create(title='Pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status=Sprint.ACTIVE, duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='test',
                                          status=Issue.NEW, sprint=self.sprint,
                                          estimation=1)

    def test_sprint_response_200(self):
        url = reverse('project:sprint_detail',
                      kwargs={'project_id': self.sprint.project_id,
                              'sprint_id': self.sprint.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/sprint_detail.html')

    def test_sprint_response_404(self):
        url = reverse('project:sprint_detail',
                      kwargs={'project_id': self.sprint.project_id,
                              'sprint_id': 1000})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

    def test_sprint_create(self):
        sprint = Sprint.objects.create(title='T_sprint',
                                       project_id=self.project.id,
                                       status=Sprint.NEW, duration=10)
        url = reverse('project:sprint_create',
                      kwargs={'project_id': sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        inst_count = len(Sprint.objects.all())
        self.assertEqual(Sprint.objects.get(pk=sprint.id).status, Sprint.NEW)
        data = {'title': "It's a New Sprint", 'project': self.project.id,
                "duration": 7, 'status': Sprint.NEW}
        response = self.client.post(url, data)
        new_sprint = Sprint.objects.get(pk=inst_count + 1)
        self.assertEquals(new_sprint.duration, 7)
        self.assertEquals(new_sprint.title, "It's a New Sprint")
        self.assertEquals(new_sprint.project, self.project)
        self.assertEquals(new_sprint.status, Sprint.NEW)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(len(Sprint.objects.all()), inst_count + 1)


class IssueResponseTests(LoginRequiredBase):
    def setUp(self):
        super(IssueResponseTests, self).setUp()
        self.project = Project.objects.create(title='Pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status=Sprint.ACTIVE, duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='test',
                                          status=Issue.NEW, sprint=self.sprint,
                                          estimation=1)

    def test_issue_response_200(self):
        url = reverse('project:issue_detail',
                      kwargs={'project_id': self.issue.project_id,
                              'issue_id': self.issue.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/issue_detail.html')

    def test_issue_response_404(self):
        url = reverse('project:issue_detail',
                      kwargs={'project_id': self.project.id, 'issue_id': 1000})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)


class ActiveSprintTests(LoginRequiredBase):
    def setUp(self):
        super(ActiveSprintTests, self).setUp()
        self.project = Project.objects.create(title='pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status=Sprint.ACTIVE, duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status=Issue.NEW, sprint=self.sprint,
                                          estimation=1)

        # it's a new test, don't delete

    def test_on_create_two_active_sprints_at_time(self):
        self.assertEqual(Sprint.objects.filter(status='active').count(), 1)
        try:
            Sprint.objects.create(project=self.project,
                                  status='active', duration=10)
        except ValidationError:
            self.assertEqual(Sprint.objects.filter(status='active').count(), 1)

    def test_project_sprint_active_response_200(self):
        self.assertEqual(Sprint.objects.get(pk=self.sprint.id).status,
                         Sprint.ACTIVE)
        url = reverse('project:sprint_active',
                      kwargs={'project_id': self.sprint.project_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project/sprint_active.html')

    def test_project_sprint_active_response_404(self):
        url = reverse('project:sprint_active', kwargs={'project_id': 1000})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertEqual(response.status_code, 200)

    def test_all_unfinished_issues_after_sprint_ends_move_to_backlog(self):
        number_of_issues = 10
        project = Project.objects.create(title='Test Project')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status='active', duration=10)
        for i in range(number_of_issues):
            Issue.objects.create(title='Test Issue {}'.format(i),
                                 project=project, order=Issue.MEDIUM,
                                 author=self.user, estimation=1)

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
            'order')[:2 + len(issue_new) + len(issue_in_progress)]
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

    def test_finish_sprint_view(self):
        project = Project.objects.create(title='Test Project')
        team = ProjectTeam.objects.create(project=project, title='Test Team')
        sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,
                                       status=Sprint.ACTIVE, duration=10)
        url = reverse('project:finish_active_sprint',
                      kwargs={'project_id': sprint.project_id})
        data = {'release_link': 'http://127.0.0.1:8000/project/1/',
                'feedback_text': 'some text'}
        response = self.client.post(url, data)
        sprint.refresh_from_db()
        self.assertEqual(sprint.release_link,
                         'http://127.0.0.1:8000/project/1/')
        self.assertEqual(sprint.feedback_text, 'some text')
        self.assertEqual(sprint.status, Sprint.FINISHED)
        self.assertEqual(response.status_code, 302)


class SprintDashboard(LoginRequiredBase):
    def setUp(self):
        super(SprintDashboard, self).setUp()
        self.project = Project.objects.create(title='pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status='active', duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status='new', sprint=self.sprint,
                                          estimation=1)

    def test_project_issue_push_responses(self):
        response = self.client.get(reverse('project:issue_push'))
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        url = reverse('project:issue_push')
        data = {'table': 'in progress', 'id': 1}
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status, 'new')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status,
                         'in progress')

        data = {'table': 'resolved', 'id': 1}
        self.client.post(url, data)
        self.assertEqual(Issue.objects.get(pk=self.issue.id).status,
                         'resolved')

        url = reverse('project:issue_push')
        data = {'table': 'new', 'id': 2}
        response = self.client.post(url, data)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        sprint2 = Sprint.objects.create(project=self.project,
                                        status='finished', duration=10)
        Issue.objects.create(project=self.project,
                             author=self.employee, title='title',
                             status='new', sprint=sprint2, estimation=1)
        url = reverse('project:issue_push')
        data = {'table': 'resolved', 'id': 2}
        response = self.client.post(url, data)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)


class ProjectNotes(LoginRequiredBase):
    def setUp(self):
        super(ProjectNotes, self).setUp()
        self.project = Project.objects.create(title='pr1')
        self.team = ProjectTeam.objects.create(project=self.project)
        self.sprint = Sprint.objects.create(project=self.project,
                                            status='active', duration=10)
        self.employee = Employee.objects.create()
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.employee, title='title',
                                          status='new', sprint=self.sprint,
                                          estimation=1)
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
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

    def test_notes_post_responses(self):
        url = reverse('project:note', kwargs={'project_id': self.project.id})
        data = {'id': 1, 'title': 'title', 'content': 'SOME TEXT#'}
        self.client.post(url, data)
        self.assertEqual(ProjectNote.objects.get(pk=1).content, 'SOME TEXT#')

        data = {'id': 2, 'title': 'title', 'content': 'SOME TEXT'}
        response = self.client.post(url, data)
        self.assertTemplateUsed(response, 'general/404.html')
        self.assertContains(response, "access not found: 404 ERROR",
                            status_code=200)

        self.assertEqual(len(ProjectNote.objects.all()), 1)
        data = {'id': 'undefined', 'title': 'title', 'content': 'SOME TEXT'}
        response = self.client.post(url, data)
        self.assertEqual('note_id' in response, True)
        self.assertEqual(len(ProjectNote.objects.all()), 2)

    def test_notes_delete_responses(self):
        url = reverse('project:note', kwargs={'project_id': self.project.id})
        data = urlencode({'id': 1})
        self.assertEqual(len(ProjectNote.objects.all()), 1)
        response = self.client.delete(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(ProjectNote.objects.all()), 0)


class WorkloadManagerTest(LoginRequiredBase):
    def setUp(self):
        super(WorkloadManagerTest, self).setUp()
        self.project = Project.objects.create()
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')
        self.team.employees.add(self.user)

    def test_workload_view_with_no_sprint(self):
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={
                                               'project_id': self.project.id,
                                               'sprint_status': Sprint.ACTIVE}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'general/404.html')

    def test_workload_view_with_empty_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,

                                       status=Sprint.ACTIVE, duration=7)
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={
                                               'project_id': self.project.id,
                                               'sprint_status': Sprint.ACTIVE,
                                               }))
        self.assertContains(response, "No items.", status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])

    def test_workload_view_with_items(self):
        sprint = Sprint.objects.create(title='title', project=self.project,
                                       start_date=datetime.date(2017, 12, 14),
                                       end_date=datetime.date(2017, 12, 21),
                                       status=Sprint.ACTIVE, duration=7)
        Issue.objects.create(project=self.project, author=self.user,
                             sprint=sprint, employee=self.user, estimation=1)
        response = self.client.get(reverse('project:workload_manager',
                                           kwargs={
                                               'project_id': self.project.id,
                                               'sprint_status': Sprint.ACTIVE}))
        self.assertContains(response, self.user.username, status_code=200)
        self.assertQuerysetEqual(response.context['items'], [])


class IssueSearchTest(LoginRequiredBase):
    def setUp(self):
        super(IssueSearchTest, self).setUp()
        self.project = Project.objects.create(title='pr1')
        for status, _ in Issue.ISSUE_STATUS_CHOICES:
            for i in range(10):
                Issue.objects.create(title='Title {} {}'.format(status, i),
                                     description='Description {} {}'.format(
                                         status, i),
                                     author=self.user,
                                     status=status,
                                     estimation=2,
                                     project=self.project)

    def test_basic_search(self):
        url = reverse('project:issue_search',
                      kwargs={'project_id': self.project.id})
        response = self.client.get(url)
        response = self.client.get(url, {'s': 'Title NEW 1'})
        self.assertTrue(response.status_code == 200)
        self.assertContains(response, 'Title NEW 1')
        self.assertNotContains(response, 'Title NEW 2')


class CreateSprintTests(LoginRequiredBase):
    def setUp(self):
        super(CreateSprintTests, self).setUp()
        self.project = Project.objects.create(title='title',
                                              start_date=datetime.date(2017, 2, 2))
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')
        self.team.employees.add(self.user)

    def test_create_sprint_with_valid_data(self):
        form_data = {'title': 'title', 'duration': 7}
        response = self.client.post(reverse('project:sprint_create',
                                            args=[self.project.id]), data=form_data)
        self.assertRedirects(response, reverse('project:workload_manager',
                                               args=[self.project.id, Sprint.NEW]),
                             status_code=302, target_status_code=200)

    def test_create_sprint_with_invalid_data(self):
        form_data = {'title': 'title', 'duration': 'word'}
        response = self.client.post(reverse('project:sprint_create',
                                            args=[self.project.id]), data=form_data)
        self.assertTemplateUsed(response, 'general/404.html')


class StartSprintTests(LoginRequiredBase):
    def setUp(self):
        super(StartSprintTests, self).setUp()
        self.project = Project.objects.create(title='title',
                                              start_date=datetime.date(2017, 2, 2))
        self.sprint = Sprint.objects.create(project=self.project, title='title',
                                            status=Sprint.NEW, duration=10)
        self.team = ProjectTeam.objects.create(project=self.project,
                                               title='title')
        self.team.employees.add(self.user)

    def test_start_sprint_if_active_one_does_not_exists(self):
        response = self.client.post(reverse('project:sprint_start',
                                            args=[self.project.id]))
        self.assertRedirects(response, reverse('project:sprint_active',
                                               args=[self.project.id, ]),
                             status_code=302, target_status_code=200)
        response = self.client.get(reverse('project:sprint_active',
                                           args=[self.project.id, ]))
        self.assertContains(response, 'Workload Manager', status_code=200)

    def test_start_sprint_if_active_one_exists(self):
        Sprint.objects.create(project=self.project, title='title',
                              start_date=datetime.date(2017, 2, 2),
                              status=Sprint.ACTIVE, duration=10)
        response = self.client.post(reverse('project:sprint_start',
                                            args=[self.project.id]))
        self.assertRedirects(response, reverse('project:sprint_active',
                                               args=[self.project.id, ]),
                             status_code=302, target_status_code=200)
        response = self.client.get(reverse('project:sprint_active',
                                           args=[self.project.id, ]))
        self.assertContains(response, 'Finish Sprint', status_code=200)
