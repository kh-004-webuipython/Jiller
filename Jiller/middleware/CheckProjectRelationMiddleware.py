import json

from django.http import HttpResponseForbidden
from django.urls import resolve
from employee.models import Employee
from project.models import ProjectTeam, Project, Issue
from re import compile

PROJECT_URLS = [compile(r'^project/.+')]
ISSUE_ORDER = compile(r'^project/issue_order/$')


class CheckProjectRelation(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def is_user_attached_to_project(self, user_id, project_id):
        project_team = ProjectTeam.objects.filter(project_id=project_id)
        for team in project_team:
            try:
                employee = ProjectTeam.objects.get(
                    pk=team.id, employees=user_id)
            except ProjectTeam.DoesNotExist:
                continue
            else:
                return True
        return False

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        if request.user.is_staff or not any(m.match(path) for m in PROJECT_URLS):
            response = self.get_response(request)
            return response

        if request.method == 'GET':
            resolved = resolve(request.path)
            if self.is_user_attached_to_project(request.user.id, resolved.kwargs['project_id']):
                response = self.get_response(request)
                return response

        if request.method == 'POST' and ISSUE_ORDER.match(path):
            issue_ids = [int(id) for id in json.loads(request.POST.get('data')).keys()]
            for issue_id in issue_ids:
                try:
                    issue = Issue.objects.get(pk=issue_id)
                except Issue.DoesNotExist:
                    break
                else:
                    if not self.is_user_attached_to_project(request.user.id, issue.project_id):
                        break
            else:
                response = self.get_response(request)
                return response

        return HttpResponseForbidden()
