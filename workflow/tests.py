from django.test import TestCase
from django.urls import reverse

from .models import Project


class ProjectMethodTests(TestCase):
    def create_project(self, title='only a test',
                       description='yes, this is only a test',
                       start_date='2017-12-14', end_date='2017-12-14'):
        return Project.objects.create(title=title, description=description,
                                      start_date=start_date, end_date=end_date)

    def test_project_creation(self):
        test_project = self.create_project()
        self.assertTrue(isinstance(test_project, Project))

    # views (uses reverse)

    # def test_project_list_view(self):
    #     w = self.create_project()
    #     url = reverse("workflow.views.ProjectListView")
    #     resp = self.client.get(url)
    #
    #     self.assertEqual(resp.status_code, 200)
    #     self.assertIn(w.title, resp.content)

    # def test_project_detail(self):
    #     response = self.client.get()
    #     self.assertEqual(response.status_code, 200)

