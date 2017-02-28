import re

class SaveLastProjectMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    """
    Set cookie with current project on every view that contains project_id
    value in it self. Wrong project_id cannot be assigned  due to other
    middleware - CheckProjectRelation
    """

    def __call__(self, request):
        response = self.get_response(request)

        user = request.user
        if user.groups.exists():
            new_cookie_name = 'Last_pr' + str(user.groups.first().pk) + '#' \
                              + str(user.id)
            path = request.path_info.lstrip('/')
            pattern = r'^project/(?P<project_id>\d+)/'
            m = re.match(pattern, path)
            if m:
                new_cookie_value = m.group('project_id')
                if request.COOKIES.get(new_cookie_name) != new_cookie_value:
                    response.set_cookie(new_cookie_name, new_cookie_value)
        return response

