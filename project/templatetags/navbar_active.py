from django import template

register = template.Library()


@register.filter(name='navbar_active')
def navbar_active(request, id):
    try:
        project_id = request.path[9]
    except IndexError:
        return False
    if request.path.startswith('/project/') \
            and project_id.isdigit() \
            and int(project_id) == id:
        return True
    return False

