from django.test import TestCase, Client

from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

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


class BacklogViewTests(LoginRequiredBase):
    def test_backlog_view_with_no_issues(self):
        project = Project.objects.create(title='title')
        response = self.client.get(reverse('workflow:backlog',
                                           kwargs={'project_id': project.id}))
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


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_page = reverse('workflow:login')
        self.client = Client()
        self.user = Employee.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword', first_name='Miss',
                                                 last_name='Mister', role='developer')

    def test_for_correct_data(self):
        response = self.client.get(self.login_page)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.login_page, {'username': 'john', 'password': 'johnpassword'})
        self.assertRedirects(response, reverse('workflow:profile'))

    def test_for_wrong_username(self):
        response = self.client.post(self.login_page,
                                    {'username': 'wrongusername', 'password': 'johnpassword'})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))

    def test_for_wrong_password(self):
        response = self.client.post(self.login_page, {'username': 'john', 'password': 't2'})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))

    def test_for_empty_password(self):
        response = self.client.post(self.login_page, {'username': 'john', 'password': ''})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.registration_page_url = reverse('workflow:registration')
        self.login_page_url = reverse('workflow:login')
        self.client = Client()
        self.username = 't1'
        self.password = 'strongandverypowerfullpassword11111'
        self.email = 'simple_email1@gmail.com'
        self.first_name = 'Ivan'
        self.last_name = 'Ivanov'
        self.role = Employee.DEVELOPER

    def get_standard_post(self):
        return {'username': self.username, 'password': self.password,
                'password_confirmation': self.password,
                'email': self.email,
                'email_confirmation': self.email,
                'last_name': self.last_name, 'first_name': self.first_name, 'role': self.role}

    def check_if_form_still_contain_info_after_error(self, response, expect_result):
        self.assertContains(response, expect_result['username'])
        self.assertContains(response, expect_result['email'])
        self.assertContains(response, expect_result['email_confirmation'])
        self.assertContains(response, expect_result['first_name'])
        self.assertContains(response, expect_result['last_name'])
        self.assertNotContains(response, expect_result['password'])
        self.assertNotContains(response, expect_result['password_confirmation'])

    def test_for_right_registration_data(self):
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        response = self.client.post(self.registration_page_url,
                                    self.get_standard_post())

        self.assertEqual(response.url, self.login_page_url)
        self.assertEqual(response.status_code, 302)
        user = Employee.objects.get(username=self.username)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.role, self.role)
        self.assertEqual(user.email, self.email)

    def test_with_wrong_email_confirmation(self):
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        post_data = self.get_standard_post()
        post_data['email_confirmation'] += '1'
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.check_if_form_still_contain_info_after_error(response, post_data)
        self.assertContains(response, _('Email does not equal confirm email'))

    def test_with_wrong_password_confirmation(self):
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        post_data = self.get_standard_post()
        post_data['password_confirmation'] += '1'
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.check_if_form_still_contain_info_after_error(response, post_data)
        self.assertContains(response, _('Password do not equal confirm password'))

    def test_username_already_exist(self):
        post_data = self.get_standard_post()
        Employee.objects.create_user(post_data['username'], 'lennon@thebeatles.com', 'johnpassword', first_name='Miss',
                                     last_name='Mister', role=post_data['role'])

        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('User with this username already exists'))

    def test_email_already_exist(self):
        post_data = self.get_standard_post()
        Employee.objects.create_user('john', post_data['email'], 'johnpassword', first_name='Miss',
                                     last_name='Mister', role=post_data['role'])
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('User with this email already exists'))

    def test_wrong_user_role(self):
        post_data = self.get_standard_post()
        post_data['role'] += '1'
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("Registration Form"))
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.check_if_form_still_contain_info_after_error(response, post_data)
        self.assertContains(response, _('Wrong user role'))
