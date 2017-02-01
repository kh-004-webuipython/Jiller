from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import ProjectTeam
from employee.models import Employee
from waffle.decorators import waffle_flag


def user_belongs_project(function):
    def wrap(request, *args, **kwargs):
        admin = Employee.objects.get(pk=request.user.id)
        if admin.is_staff:
            return function(request, *args, **kwargs)

        project_team = ProjectTeam.objects.filter(project_id=kwargs['project_id'])
        for team in project_team:
            try:
                employee = ProjectTeam.objects.get(
                    pk=team.id, employees=request.user.id)
            except ProjectTeam.DoesNotExist:
                return HttpResponseRedirect(reverse('project:list'))
            if employee:
                return function(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('project:list'))
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


edit_project_detail = [user_belongs_project,
                       waffle_flag('edit_project_detail', 'project:list')]

create_sprint = [user_belongs_project,
                 waffle_flag('create_sprint', 'project:list')]

create_project = [waffle_flag('create_project', 'project:list')]

delete_project = [waffle_flag('project:list', 'project:list')]

