from django import template

from employee.models import IssueLog
from project.models import Issue, Project, IssueComment

register = template.Library()


@register.filter(name='security_list')
def security_note_list(data, user):
    if data:
        if data.model == Issue:
            return data.filter(project__in=user.get_all_projects()).order_by('-order')
        if data.model == Project:
            return data.filter(id__in=user.get_all_projects())
        if data.model == IssueLog or data.model == IssueComment:
            return data.filter(issue__project__in=user.get_all_projects())
    return []
