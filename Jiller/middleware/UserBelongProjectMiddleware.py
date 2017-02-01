from django.http import HttpResponseRedirect
from django.urls import reverse
from project.models import ProjectTeam
from employee.models import Employee


class LoginRequiredMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        return response
