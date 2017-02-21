from django import template

register = template.Library()


@register.filter(name='navbar_active')
def navbar_active(request, id):
    if request.path.startswith('/project/') \
            and request.path[9].isdigit() \
            and int(request.path[9]) == id:
        return True
    return False

