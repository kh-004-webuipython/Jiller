from django import template

from project.models import Issue

register = template.Library()


@register.filter(name='security_note_list')
def security_note_list(data, user):
    return data.filter(issue__project__in=user.get_all_projects())


@register.filter(name='security_issue_list')
def security_issue_list(data, user):
    return data.filter(project__in=user.get_all_projects()).exclude(status__in=(Issue.RESOLVED, Issue.CLOSED))


@register.filter(name='security_project_list')
def security_project_list(data, user):
    return data.filter(id__in=user.get_all_projects())
