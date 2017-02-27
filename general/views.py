from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, Http404

from employee.models import Employee
from .forms import LoginForm, RegistrationForm
from .email_confirmation import sender


def home_page(request):
    return render(request, 'general/home_page.html')


def login_form_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                if user.is_confirmed:
                    login(request, user)

                    # make redirect to last project from cookie
                    if user.groups.all():
                        role_pk = user.groups.all()[0].pk
                        cookie_name = 'Last_pr' + str(role_pk) + '#' + \
                                      str(user.id)

                        if cookie_name in request.COOKIES:
                            last_project = request.COOKIES.get(cookie_name)
                            # make future redirects depend by role
                            if role_pk == 1:
                                return redirect('project:sprint_active',
                                                project_id=int(last_project))
                            elif role_pk == 2:
                                return redirect('project:sprint_active',
                                                project_id=int(last_project))
                            elif role_pk == 3:
                                return redirect('project:backlog',
                                                project_id=int(last_project))
                            elif role_pk == 4:
                                return redirect('project:team',
                                                project_id=int(last_project))

                    return redirect('general:home_page')
                else:
                    return render(request, 'general/require_key.html', {'user': user})

        messages.error(request, _("Wrong username or password"))
        return redirect('general:login')
    else:
        form = LoginForm()
    return render(request, 'general/login.html', {'form': form})


def registration_form_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            photo = form.cleaned_data['photo']
            employee = Employee.objects.create_user(username, email, password,
                                                    last_name=last_name,
                                                    first_name=first_name,
                                                    photo=photo)
            if role != RegistrationForm.PROJECT_MANAGER:
                employee.groups.add(Group.objects.get(name=role))
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
    sender(request, user.email, username, user.confirmation_key)
    messages.add_message(request, messages.INFO,
                         _("Confirmation code has been sent to your email."))
    return redirect('general:login')


def handler400(request):
    return render(request, 'general/400.html')


def handler403(request):
    return render(request, 'general/403.html')


def handler404(request):
    return render(request, 'general/404.html')


def handler500(request):
    return render(request, 'general/500.html')
