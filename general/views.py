from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, Http404

from employee.models import Employee
from .forms import LoginForm, RegistrationForm
from .email_confirmation import sender


def home_page(request):
    return render(request, 'general/home_page.html')


def profile(request):
    return render(request, 'general/profile.html')


def login_form_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_confirmed:
                    login(request, user)
                    return redirect('general:profile')
                else:
                    return render(request, 'general/require_key.html', {'user': user})

        messages.error(request, _("Wrong username or password"))
        return redirect('general:login')
    else:
        form = LoginForm()
    return render(request, 'general/login.html', {'form': form})


def registration_form_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            Employee.objects.create_user(username, email, password,
                                         last_name=last_name,
                                         first_name=first_name,
                                         role=role)
            return HttpResponseRedirect(reverse('general:sender',
                                                kwargs={'username': username}))
    else:
        form = RegistrationForm()
    return render(request, 'general/registration.html', {'form': form})


def user_logout_view(request):
    logout(request)
    return redirect('general:login')


def email_confirmation(request, username, key):
    try:
        user = Employee.objects.filter(username=username).first()
    except Employee.DoesNotExist:
        raise Http404("Username does not exist")

    if user.is_confirmed:
        return redirect('project:list')
    else:
        try:
            user.confirm_email(key)
        except:
            return render(request, 'general/require_key.html', {'user': user})
        if user.is_confirmed:
            return redirect('project:list')
    return render(request, 'general/require_key.html', {'user': user})


def send_to(request, username):
    user = Employee.objects.filter(username=username).first()
    sender(user.email, username, user.confirmation_key)
    messages.add_message(request, messages.INFO,
                         _("Confirmation code has been sent to your email."))
    return redirect('general:login')
