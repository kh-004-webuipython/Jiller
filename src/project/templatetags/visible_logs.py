from django import template

register = template.Library()


@register.filter(name='visible_logs')
def visible_logs(logs, count=False):
    if count:
        return logs.filter(is_hidden=False).count()
    return logs.filter(is_hidden=False)
