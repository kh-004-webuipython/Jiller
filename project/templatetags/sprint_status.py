from django import template
from project.models import Sprint

register = template.Library()


@register.filter(name='sprint_status')
def sprint_status(status):
    if status == 'active':
        return Sprint.ACTIVE
    elif status == 'new':
        return Sprint.NEW
