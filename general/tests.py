from django.urls import reverse

from employee.models import Employee
from project.tests import LoginRequiredBase


class ProfileViewTests(LoginRequiredBase):
    def test_profile_view_with_correct_user(self):
        response = self.client.get(reverse('workflow:profile'))
        self.assertContains(response, 'Miss', status_code=200)

    def test_profile_view_with_incorrect_user(self):
        self.user = Employee.objects.create_user('mark', 'webber@redbull.com', 'markpassword', first_name='Kiss',
                                                 last_name='Dismiss', role=self.user_role_init)
        response = self.client.get(reverse('workflow:profile'))
        self.assertNotContains(response, 'Kiss')
