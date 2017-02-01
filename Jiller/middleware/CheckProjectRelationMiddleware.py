from django.db.models.query import EmptyQuerySet
from django.http import HttpResponseForbidden
from django.conf import settings
from re import compile

from django.urls import resolve
from django.urls import reverse

from project.models import ProjectTeam

PROJECT_URLS = [compile(r'^project/.+')]


class CheckProjectRelation(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lstrip('/')
        if request.user.is_staff or not any(m.match(path) for m in PROJECT_URLS):
            response = self.get_response(request)
            return response

        resolved = resolve(request.path)
        try:
            project_team = ProjectTeam.objects.filter(project_id=resolved.kwargs['project_id'])
            if not isinstance(project_team, EmptyQuerySet):
                for team in project_team:
                    try:
                        employee = ProjectTeam.objects.get(
                            pk=team.id, employees=request.user.id)
                    except:
                        return HttpResponseForbidden()
                    else:
                        response = self.get_response(request)
                        return response
        except:
            return HttpResponseForbidden()
        return HttpResponseForbidden()
