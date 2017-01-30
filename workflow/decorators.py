from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ProjectTeam
from waffle.decorators import waffle_flag


def user_belongs_project(function):
    def wrap(request, *args, **kwargs):
        project_team = ProjectTeam.objects.filter(project_id=kwargs['project_id'])
        for _ in project_team:
            employee = ProjectTeam.objects.get(employees=request.user.id)
            if employee:
                return function(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('workflow:projects'))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


edit_project_detail = [user_belongs_project,
                       waffle_flag('edit_project_detail', 'workflow:projects')]

create_sprint = [user_belongs_project,
                 waffle_flag('create_sprint', 'workflow:projects')]

create_project = [waffle_flag('create_project', 'workflow:projects')]

