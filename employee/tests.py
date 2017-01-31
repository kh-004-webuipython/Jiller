from django.core.urlresolvers import reverse

from .models import Employee
from project.tests import LoginRequiredBase


class EmployeeTest(LoginRequiredBase):
    def test_employee_list_view(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('employee:list'))
        self.assertEquals(response.status_code, 200)
        employee_list = Employee.objects.all()
        employee_context_list = response.context['employee_list']
        self.assertListEqual(sorted(employee_list), sorted(employee_context_list))

    def test_employee_detail_view(self):
        employee = Employee.objects.first()
        view_url = reverse('employee:detail', args=[employee.id])
        self.client.login(username='user', password='test')
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(employee.id, response.context['employee'].id)
