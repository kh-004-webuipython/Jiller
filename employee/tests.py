from django.core.urlresolvers import reverse

from employee.tables import EmployeeTable
from project.models import Project, Issue
from .models import Employee
from project.tests import LoginRequiredBase


class EmployeeTest(LoginRequiredBase):
    def test_employee_list_view(self):
        self.client.login(username='user', password='test')
        response = self.client.get(reverse('employee:list'))
        self.assertEquals(response.status_code, 200)
        table = EmployeeTable(Employee.objects.all())
        context_table = response.context['table']
        self.assertListEqual(table.as_values(), context_table.as_values())

    def test_employee_detail_view(self):
        employee = Employee.objects.first()
        view_url = reverse('employee:detail', args=[employee.id])
        self.client.login(username='user', password='test')
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(employee.id, response.context['employee'].id)


class IssueLogCreateTest(LoginRequiredBase):
    def setUp(self):
        super(IssueLogCreateTest, self).setUp()
        self.project = Project.objects.create(title="Project test")
        self.issue = Issue.objects.create(project=self.project,
                                          author=self.user, estimation=10, title='title')
        self.view_url = reverse('project:issue_detail', args=[self.project.id, self.issue.id])

    def test_issue_log_create_invalid_data(self):
        data = {'log': '1', 'cost': '11', 'note': ''}
        response = self.client.post(self.view_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        data = {'log': '1', 'cost': '5', 'note': ''}
        response = self.client.post(self.view_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        data = {'log': '1', 'cost': '-1', 'note': ''}
        response = self.client.post(self.view_url, data, format='json')
        self.assertEqual(response.status_code, 400)

