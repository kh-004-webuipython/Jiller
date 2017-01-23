from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect

from workflow.models import Employee


def index(request):
    return render(request, 'workflow/index.html')


def login_form(request):
    return render(request, 'workflow/login.html')


def login_proceed(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('workflow:profile')
    else:
        messages.error(request, _("Wrong username or password"))
        return redirect('workflow:login')


def registration_form(request):
    return render(request, 'workflow/registration.html')


def registration_proceed(request):
    username = request.POST['username']
    password = request.POST['password']
    last_name = request.POST['last_name']
    first_name = request.POST['first_name']
    email = request.POST['email']
    empl = Employee.objects.create_user(username, email, password, last_name=last_name, first_name=first_name)
    return redirect('workflow:profile')
