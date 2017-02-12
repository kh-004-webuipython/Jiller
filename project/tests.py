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


# class IssueFormTests(LoginRequiredBase):
#     def setUp(self):
#         super(IssueFormTests, self).setUp()
#         self.project = Project.objects.create()
#         self.employee = Employee.objects.create()
#         self.issue = Issue.objects.create(project=self.project,
#                                           author=self.employee)
#
#     def test_form_is_valid_with_empty_fields(self):
#         """
#              method should return False if fields are empty
#         """
#         form = IssueForm(project=self.project)
#         self.assertEqual(form.is_valid(), False)
#
#     def test_form_is_valid_with_not_null_required_fields(self):
#         """
#              method should return True if required fields are full
#         """
#         form_data = {'title': 'new issue'}
#         form = IssueForm(project=self.project,data=form_data)
#         self.assertEqual(form.is_valid(), True)
#
#     def test_form_is_valid_with_not_null_some_required_fields(self):
#         """
#              method should return False if some required fields are empty
#         """
#         form_data = {}
#         form = IssueForm(project=self.project,data=form_data)
#         self.assertEqual(form.is_valid(), False)
#
#     def test_form_is_valid_with_all_fields_are_full(self):
#         """
#              method should return True if all fields are full right
#         """
#         form_data = {'root': self.issue.pk,'employee': self.employee.pk,
#                      'title': 'new issue', 'description': 'description',
#                      'status': self.issue.status, 'estimation': 2
#                      }
#         form = IssueForm(project=self.project,data=form_data)
#         self.assertEqual(form.is_valid(), True)
#
#
# class IssueEditViewTests(LoginRequiredBase):
#     def setUp(self):
#         super(IssueEditViewTests, self).setUp()
#         self.client = Client()
#         self.project = Project.objects.create()
#         self.employee = Employee.objects.create()
#         self.issue = Issue.objects.create(project=self.project,
#                                           author=self.employee, title='title')
#
#     def test_issue_edit_view_use_right_template(self):
#         """
#             method should return OK if it use right template
#         """
#         response = self.client.post(
#             reverse('project:issue_edit', args=[self.project.pk,
#                                                 self.issue.pk]))
#         self.assertTemplateUsed(response, 'project/issue_edit.html')
#
#     def test_issue_edit_view_can_get_object(self):
#         """
#             method should be True and return title if it can get an object
#         """
#         issue = get_object_or_404(Issue, pk=self.issue.pk,
#                                   project=self.project.pk)
#         self.assertTrue(isinstance(issue, Issue))
#         self.assertEqual(issue.__str__(), issue.title)
#
#         # def test_issue_edit_view_cant_get_object(self):
#         #     """
#         #         method should return False if it cant get an object
#         #     """
#         #     try:
#         #         issue = get_object_or_404(Issue, pk=0, project=0)
#         #     except Issue.DoesNotExist:
#         #         raise Http404("Project does not exist")
#         #     self.assertTrue(isinstance(issue, Issue), False)
#
#
# class IssueCreateViewTests(LoginRequiredBase):
#     def setUp(self):
#         super(IssueCreateViewTests, self).setUp()
#         self.client = Client()
#         self.project = Project.objects.create()
#         self.employee = Employee.objects.create()
#         self.issue = Issue.objects.create(project=self.project,
#                                           author=self.employee, title='title')
#
#     def test_issue_create_view_use_right_template(self):
#         """
#             method should return OK if it use right template
#         """
#         response = self.client.post(
#             reverse('project:issue_create', args=[self.project.pk]))
#         self.assertTemplateUsed(response, 'project/issue_create.html')
#
#
# class ProjectsListViewTests(LoginRequiredBase):
#     def test_projectlist_view_with_no_projects(self):
#         response = self.client.get(reverse('project:list'))
#         self.assertContains(response, "There is no projects yet.",
#                             status_code=200)
#         self.assertQuerysetEqual(response.context['project_list'], [])
#
#     def test_projectlist_view_with_projects(self):
#         project = Project.objects.create(title='title')
#         response = self.client.get(reverse('project:list'))
#         self.assertQuerysetEqual(response.context['project_list'],
#                                  ['<Project: title>'])
#
#
# class BacklogViewTests(LoginRequiredBase):
#     def test_backlog_view_with_no_issues(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         response = self.client.get(reverse('project:backlog',
#                                            kwargs={'project_id': project.id}))
#         self.assertContains(response, "No issues.")
#         self.assertEqual(response.status_code, 200)
#         self.assertQuerysetEqual(response.context['issues'], [])
#
#     def test_backlog_view_with_issues(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         employee = Employee.objects.create()
#         Issue.objects.create(project=project,
#                              author=employee, title='title')
#         response = self.client.get(reverse('project:backlog',
#                                            args=[project.id, ]))
#         self.assertQuerysetEqual(response.context['issues'],
#                                  ['<Issue: title>'])
#
#     def test_backlog_view_with_issues_which_belongs_to_sprint(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         employee = Employee.objects.create()
#         team = ProjectTeam.objects.create(project=project, title='title')
#         sprint = Sprint.objects.create(title='title', project=project)
#         Issue.objects.create(project=project, author=employee,
#                              title='title', sprint=sprint)
#         response = self.client.get(reverse('project:backlog',
#                                            args=[project.id, ]))
#         self.assertQuerysetEqual(response.context['issues'], [])
#
#     def test_backlog_view_with_nonexistent_project(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         response = self.client.get(reverse('project:backlog',
#                                            args=[project.id + 1, ]))
#         self.assertEqual(response.status_code, 404)
#
#
# class SprintsListViewTests(LoginRequiredBase):
#     def test_sprints_list_view_with_no_sprint(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         response = self.client.get(reverse('project:sprints_list',
#                                            args=[project.id, ]))
#         self.assertContains(response, "No sprints.")
#         self.assertEqual(response.status_code, 200)
#         self.assertQuerysetEqual(response.context['sprints'], [])
#
#     def test_sprints_list_view_with_sprint(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         Sprint.objects.create(title='title', project=project)
#         response = self.client.get(reverse('project:sprints_list',
#                                            args=[project.id, ]))
#         self.assertQuerysetEqual(response.context['sprints'],
#                                  ['<Sprint: title>'])
#
#     def test_sprints_list_view_must_not_consist_active_sprint(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         team = ProjectTeam.objects.create(project=project, title='title')
#         Sprint.objects.create(title='title', project=project, status=Sprint.ACTIVE)
#         response = self.client.get(reverse('project:sprints_list',
#                                            args=[project.id, ]))
#         self.assertQuerysetEqual(response.context['sprints'], [])
#
#     def test_sprints_list_view_with_nonexistent_project(self):
#         project = Project.objects.create(title='title',
#                                          start_date=datetime.date(
#                                              2017, 12, 14))
#         response = self.client.get(reverse('project:sprints_list',
#                                            args=[project.id + 1, ]))
#         self.assertEqual(response.status_code, 404)
#
#
# class ProjectViewTests(LoginRequiredBase):
#     def setUp(self):
#         # Set up data for the whole TestCase
#         super(ProjectViewTests, self).setUp()
#         self.project = Project.objects.create(title='only a test',
#                                               description='yes, this is only a test',
#                                               start_date=datetime.date(
#                                                   2017, 12, 14),
#                                               end_date=datetime.date(
#                                                   2017, 12, 14))
#
#         # create
#
#     def test_project_create(self):
#         response = self.client.get(reverse('project:create'))
#         self.assertEqual(response.status_code, 200)
#
#     def test_check_how_many_objects_are_in_db_now(self):
#         all_projects_in_database = Project.objects.all()
#         self.assertEquals(all_projects_in_database.count(), 1)
#
#     def test_check_all_project_attributes(self):
#         only_project_in_database = Project.objects.all()[0]
#         self.assertEquals(only_project_in_database, self.project)
#         self.assertEquals(only_project_in_database.title,
#                           'only a test')
#         self.assertEquals(only_project_in_database.description,
#                           'yes, this is only a test')
#         self.assertEquals(only_project_in_database.start_date,
#                           self.project.start_date)
#         self.assertEquals(only_project_in_database.end_date,
#                           self.project.end_date)
#
#         # update
#
#     def test_project_update_page(self):
#         test_project = self.project
#         response = self.client.post(
#             reverse('project:update',
#                     kwargs={'project_id': test_project.id}))
#         self.assertEqual(response.status_code, 200)
#
#     def test_project_update_valid(self):
#         test_project = Project.objects.all()[0]
#         date = datetime.datetime.strptime('24052010', "%d%m%Y").date()
#         form_data = {'title': test_project.title + '123',
#                      'description': test_project.description + '123',
#                      'start_date': date + datetime.timedelta(
#                          days=1),
#                      'end_date': date + datetime.timedelta(
#                          days=2)}
#         response = self.client.post(
#             reverse('project:update',
#                     kwargs={'project_id': test_project.id}), data=form_data)
#         url_detail = reverse('project:detail',
#                              kwargs={'project_id': test_project.id})
#         self.assertRedirects(response, url_detail, status_code=302,
#                              target_status_code=200)
#         test_project = Project.objects.all()[0]
#         self.assertEquals(test_project.title, 'only a test123')
#         self.assertEquals(test_project.title, 'only a test123')
#         self.assertEquals(test_project.description,
#                           'yes, this is only a test123')
#         self.assertEquals(test_project.start_date,
#                           date + datetime.timedelta(
#                               days=1))
#         self.assertEquals(test_project.end_date,
#                           date + datetime.timedelta(
#                               days=2))
#
#     def test_incorrect_date(self):
#         test_project = Project.objects.all()[0]
#         date = datetime.datetime.strptime('24052010', "%d%m%Y").date()
#         form_data = {'start_date': date + datetime.timedelta(
#             days=5),
#                      'end_date': date + datetime.timedelta(
#                          days=2)}
#         response = self.client.post(
#             reverse('project:update',
#                     kwargs={'project_id': test_project.id}), data=form_data)
#         test_project = Project.objects.all()[0]
#         self.assertNotEquals(test_project.start_date,
#                           date + datetime.timedelta(
#                               days=5))
#
#         # delete
#
#     def test_project_delete_page(self):
#         test_project = self.project
#         response = self.client.get(
#             reverse('project:delete',
#                     kwargs={'project_id': test_project.id}))
#         self.assertEqual(response.status_code, 200)
#
#     def test_project_is_really_deleted(self):
#         test_project = Project.objects.all()[0]
#         response = self.client.post(
#             reverse('project:delete',
#                     kwargs={'project_id': test_project.id}))
#         url_detail = reverse('project:list')
#         self.assertRedirects(response, url_detail, status_code=302,
#                              target_status_code=200)
#         test_project = Project.objects.all()[0]
#         self.assertEquals(test_project.is_active, False)
#
#     # detail
#
#     def test_project_detail_page(self):
#         test_project = self.project
#         response = self.client.get(
#             reverse('project:detail',
#                     kwargs={'project_id': test_project.id}))
#         self.assertEqual(response.status_code, 200)
#
#
# class SprintResponseTests(LoginRequiredBase):
#     def test_project_sprint_response_200(self):
#         project = Project.objects.create(title='Test Project')
#         ProjectTeam.objects.create(project=project, title='Test Team')
#         sprint = Sprint.objects.create(title='T_sprint', project_id=project.id, status='new')
#         url = reverse('project:sprint_detail',
#                       kwargs={'project_id': sprint.project_id,
#                               'sprint_id': sprint.id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def test_project_sprint_response_404(self):
#         url = reverse('project:sprint_detail', kwargs={'project_id': 100,
#                                                        'sprint_id': 100})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#     def test_project_sprint_create(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,status='new')
#         url = reverse('project:sprint_create',
#                       kwargs={'project_id': sprint.project_id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         inst_count = len(Sprint.objects.all())
#         self.assertEqual(Sprint.objects.get(pk=1).status, 'new')
#         start_date = datetime.datetime.now().strftime("%Y-%m-%d")
#         end_date = datetime.datetime.now() + datetime.timedelta(days=14)
#         end_date = end_date.strftime("%Y-%m-%d")
#         data = {'title': "It's a New Sprint", 'project': project.id,
#                 "start_date": start_date, "end_date": end_date,'status':'new'}
#         response = self.client.post(url, data)
#         new_sprint = Sprint.objects.get(pk=2)
#         self.assertEquals(new_sprint.start_date.strftime("%Y-%m-%d"),
#                           start_date)
#         # self.assertEquals(new_sprint.end_date.strftime("%Y-%m-%d"), end_date)
#         self.assertEquals(response.status_code, 302)
#         self.assertEquals(len(Sprint.objects.all()), inst_count + 1)
#
#         # will not pass, cuz there no such functionality
#         """
#         self.assertEqual(Sprint.objects.get(pk=1).order, 1)
#         self.assertEqual(Sprint.objects.get(pk=2).order, 2)
#         self.assertEqual(Sprint.objects.get(pk=2).status, 'new')
#         """
#
#
# class IssueResponseTests(LoginRequiredBase):
#     def test_project_issue_response_200(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         Sprint.objects.create(title='T_sprint', project_id=project.id, status='new')
#         issue = Issue.objects.create(sprint_id=1, title='T_issue', author_id=1,
#                                      project_id=1,
#                                      status='new')
#         url = reverse('project:issue_detail',
#                       kwargs={'project_id': issue.project_id,
#                               'issue_id': issue.id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def test_project_issue_response_404(self):
#         url = reverse('project:issue_detail',
#                       kwargs={'project_id': 100, 'issue_id': 100})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#     def test_using_html_on_issue(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         Sprint.objects.create(title='T_sprint', project_id=project.id, status='new')
#         issue = Issue.objects.create(sprint_id=1, title='T_issue', author_id=1,
#                                      project_id=1,
#                                      status='new')
#         url = reverse('project:issue_detail',
#                       kwargs={'project_id': issue.project_id,
#                               'issue_id': issue.id})
#         response = self.client.get(url)
#         self.assertTemplateUsed(response, 'project/issue_detail.html')
#
#
# class ActiveSprintTests(LoginRequiredBase):
#     def test_project_sprint_active_response_200(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,status='active')
#         self.assertEqual(Sprint.objects.get(pk=1).status, 'active')
#         url = reverse('project:sprint_active',
#                       kwargs={'project_id': sprint.project_id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#
#     def test_project_sprint_active_response_404(self):
#         Project.objects.create(title='Test Project')
#         url = reverse('project:sprint_active', kwargs={'pk': 100})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#
# class SprintDashboard(LoginRequiredBase):
#     def test_project_issue_push_response_302(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         sprint = Sprint.objects.create(title='T_sprint', project_id=project.id,status='new')
#         iss_new = Issue.objects.create(sprint_id=1, title='T_issue',
#                                        author_id=1, project_id=1,
#                                        status='new')
#         iss_res = Issue.objects.create(sprint_id=1, title='T_issue',
#                                        author_id=1, project_id=1,
#                                        status='resolved')
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_new.project_id,
#                               'issue_id': iss_new.id, 'slug': 'right'})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 302)
#         url_redirect = reverse('project:sprint_active',
#                                kwargs={'project_id': sprint.project_id})
#         self.assertEqual(response['Location'], url_redirect)
#
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_res.project_id,
#                               'issue_id': iss_res.id, 'slug': 'left'})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 302)
#         url_redirect = reverse('project:sprint_active',
#                                kwargs={'project_id': sprint.project_id})
#         self.assertEqual(response['Location'], url_redirect)
#
#     def test_project_issue_push_right(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         Sprint.objects.create(title='T_sprint', project_id=project.id,status='active')
#         iss_new = Issue.objects.create(sprint_id=1, title='T_issue',
#                                        author_id=1, project_id=1,
#                                        status='new')
#         self.assertEqual(iss_new.status, 'new')
#
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_new.project_id,
#                               'issue_id': iss_new.id, 'slug': 'right'})
#         self.client.get(url)
#
#         changed_issue = Issue.objects.get(pk=iss_new.id)
#         self.assertEqual(changed_issue.status, 'in progress')
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_new.id)
#         self.assertEqual(changed_issue.status, 'resolved')
#
#         iss_prog = Issue.objects.create(sprint_id=1, title='T_issue',
#                                         author_id=1, project_id=1,
#                                         status='in progress')
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_prog.project_id,
#                               'issue_id': iss_prog.id, 'slug': 'right'})
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_prog.id)
#         self.assertEqual(changed_issue.status, 'resolved')
#
#         # check incorrect push to right
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_prog.id)
#         self.assertEqual(changed_issue.status, 'resolved')
#         self.assertEqual(len(Issue.objects.all()), 2)
#
#     def test_project_issue_push_left(self):
#         project = Project.objects.create(title='Test Project')
#         team = ProjectTeam.objects.create(project=project, title='Test Team')
#         Sprint.objects.create(title='T_sprint', project_id=project.id,status='active')
#         iss_res = Issue.objects.create(sprint_id=1, title='T_issue',
#                                        author_id=1, project_id=1,
#                                        status='resolved')
#         self.assertEqual(iss_res.status, 'resolved')
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_res.project_id,
#                               'issue_id': iss_res.id, 'slug': 'left'})
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_res.id)
#         self.assertEqual(changed_issue.status, 'in progress')
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_res.id)
#         self.assertEqual(changed_issue.status, 'new')
#
#         iss_prog = Issue.objects.create(sprint_id=1, title='T_issue',
#                                         author_id=1, project_id=1,
#                                         status='in progress')
#         url = reverse('project:issue_push',
#                       kwargs={'project_id': iss_prog.project_id,
#                               'issue_id': iss_prog.id, 'slug': 'left'})
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_prog.id)
#         self.assertEqual(changed_issue.status, 'new')
#
#         #  check incorrect push to left
#         self.client.get(url)
#         changed_issue = Issue.objects.get(pk=iss_prog.id)
#         self.assertEqual(changed_issue.status, 'new')
#         self.assertEqual(len(Issue.objects.all()), 2)
