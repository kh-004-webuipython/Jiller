from django.core import mail
from django.core.management import call_command
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from employee.models import Employee
from general.tasks import send_assign_email_task
from project.forms import IssueForm, IssueFormForEditing
from project.models import Project, Issue, ProjectTeam
from project.tests import LoginRequiredBase


class LoginViewTests(TestCase):
    def setUp(self):
        self.login_page = reverse('general:login')
        self.client = Client()
        self.user = Employee.objects.create_user('john',
                                                 'lennon@thebeatles.com',
                                                 'johnpassword',
                                                 first_name='Miss',
                                                 last_name='Mister')
        call_command('loaddata', 'project/fixtures/test.json', verbosity=1)

    def test_for_correct_data(self):
        response = self.client.get(self.login_page)
        self.assertEqual(response.status_code, 200)
        response = self.client.post(self.login_page, {'username': 'john',
                                                      'password': 'johnpassword'})
        print(response)
        self.assertRedirects(response, reverse('general:home_page'))

    def test_for_wrong_username(self):
        response = self.client.post(self.login_page,
                                    {'username': 'wrongusername',
                                     'password': 'johnpassword'})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))

    def test_for_wrong_password(self):
        response = self.client.post(self.login_page,
                                    {'username': 'john', 'password': 't2'})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))

    def test_for_empty_password(self):
        response = self.client.post(self.login_page,
                                    {'username': 'john', 'password': ''})
        self.assertEqual(response.url, self.login_page)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(response.url)
        self.assertContains(response, _('Wrong username or password'))


class RegistrationViewTests(TestCase):
    def setUp(self):
        self.registration_page_url = reverse('general:registration')
        self.login_page_url = reverse('general:login')
        self.client = Client()
        self.username = 't1'
        self.password = 'strongandverypowerfullpassword11111'
        self.email = 'simple_email1@gmail.com'
        self.first_name = 'Ivan'
        self.last_name = 'Ivanov'
        self.role = 'developer'

        self.login_page = reverse('general:login')
        self.client = Client()
        self.user = Employee.objects.create_user('john1',
                                                 'lennon@thebatles.com',
                                                 'johnpassword',
                                                 first_name='Miss',
                                                 last_name='Mister')
        call_command('loaddata', 'project/fixtures/test.json', verbosity=1)

    def get_standard_post(self):
        return {'username': self.username, 'password': self.password,
                'password_confirmation': self.password,
                'email': self.email,
                'email_confirmation': self.email,
                'last_name': self.last_name, 'first_name': self.first_name,
                'role': self.role}

    def check_if_form_still_contain_info_after_error(self, response,
                                                     expect_result):
        self.assertContains(response, expect_result['username'])
        self.assertContains(response, expect_result['email'])
        self.assertContains(response, expect_result['email_confirmation'])
        self.assertContains(response, expect_result['first_name'])
        self.assertContains(response, expect_result['last_name'])
        self.assertNotContains(response, expect_result['password'])
        self.assertNotContains(response,
                               expect_result['password_confirmation'])

    def test_for_right_registration_data(self):
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("New User Registration"))
        response = self.client.post(self.registration_page_url,
                                    self.get_standard_post())
        user = Employee.objects.get(username=self.username)
        self.assertEqual(user.username, self.username)
        self.assertEqual(user.last_name, self.last_name)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.email, self.email)

    def test_with_wrong_password_confirmation(self):
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("New User Registration"))
        post_data = self.get_standard_post()
        post_data['password_confirmation'] += '1'
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.check_if_form_still_contain_info_after_error(response, post_data)
        self.assertContains(response,
                            _('Password do not equal confirm password'))

    def test_username_already_exist(self):
        post_data = self.get_standard_post()
        Employee.objects.create_user(post_data['username'],
                                     'lennon@thebeatles.com', 'johnpassword',
                                     first_name='Miss',
                                     last_name='Mister')

        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("New User Registration"))
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            _('User with this username already exists'))

    def test_email_already_exist(self):
        post_data = self.get_standard_post()
        Employee.objects.create_user('john', post_data['email'],
                                     'johnpassword', first_name='Miss',
                                     last_name='Mister')
        response = self.client.get(self.registration_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _("New User Registration"))
        response = self.client.post(self.registration_page_url, post_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, _('User with this email already exists'))


class ProfileViewTests(LoginRequiredBase):
    def test_profile_view_with_correct_user(self):
        response = self.client.get(reverse('general:home_page'))
        self.assertContains(response, 'Miss', status_code=200)

    def test_profile_view_with_incorrect_user(self):
        self.user = Employee.objects.create_user('mark', 'webber@redbull.com',
                                                 'markpassword',
                                                 first_name='Kiss',
                                                 last_name='Dismiss')
        response = self.client.get(reverse('general:home_page'))
        self.assertNotContains(response, 'Kiss')


class AssignEmailTests(LoginRequiredBase):
    def setUp(self):
        super(AssignEmailTests, self).setUp()

    def test_check_assign_email(self):
        self.project = Project.objects.create()

        self.issue = Issue.objects.create(project=self.project,
                                          author=self.user, estimation=1)
        base_url= 'example.com'
        send_assign_email_task(base_url,self.user.email, self.user.id, self.issue.id)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Jiller notification')
        self.assertEqual(mail.outbox[0].from_email,
                         settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
