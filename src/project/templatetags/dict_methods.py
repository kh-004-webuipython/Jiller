from django import template

register = template.Library()


@register.filter(name='getlist')
def get_list(GET, key):
    return GET.getlist(key)