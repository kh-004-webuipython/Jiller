from django import template
from project.models import Sprint

register = template.Library()


@register.filter(name='sprint_exist')
def sprint_exist(project_id, status):
    flag = False
    sprint = Sprint.objects.filter(project=project_id, status=status)
    if sprint:
        flag = True
    return flag
