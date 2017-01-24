from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect
from django.http import Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.urls import reverse_lazy

from .forms import LoginForm, RegistrationForm
from .models import Employee
from .models import Project
from .models import Issue, Sprint


def index(request):
    return render(request, 'workflow/index.html')


def issue(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id, project=project_id)
    return render(request, 'workflow/issue.html', {
        'issue': current_issue, 'project_id': project_id, 'issue_id': issue_id
    })


class SprintView(DetailView):
    model = Sprint
    template_name = 'workflow/sprint.html'
    query_pk_and_slug = True
    pk_url_kwarg = 'sprint_id'
    slug_field = 'project'
    slug_url_kwarg = 'project_id'

    def get_context_data(self, **kwargs):
        context = super(SprintView, self).get_context_data(**kwargs)
        cur_proj = self.kwargs['project_id']
        cur_spr = self.kwargs['sprint_id']
        issues_from_this_sprint = Issue.objects.filter(project_id=cur_proj,
                                                       sprint_id=cur_spr)
        context['new_issues'] = issues_from_this_sprint.filter(status="new")
        context['in_progress_issues'] = \
            issues_from_this_sprint.filter(status="in progress")
        context['resolved_issues'] = \
            issues_from_this_sprint.filter(status="resolved")
        return context

def login_form(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('workflow:profile')
            else:
                messages.error(request, _("Wrong username or password"))
                return redirect('workflow:login')
    else:
        form = LoginForm()
    return render(request, 'workflow/login.html', {'form': form})



def registration_form(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            employee = Employee.objects.create_user(username, email, password, last_name=last_name, first_name=first_name)
            return redirect('workflow:profile')

    form = RegistrationForm()
    return render(request, 'workflow/registration.html')



def project_detail(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, 'workflow/project_detail.html',
                  {'project': project})


def projtest(request):
    return render(request, 'workflow/project_navbar.html')


class ProjectDetail(DetailView):
    queryset = Project.objects.all()

    def get_object(self):
        object = super(ProjectDetail, self).get_object()
        return object


class ProjectCreate(CreateView):
    model = Project
    fields = ['title', 'end_date']
    template_name_suffix = '_create_form'


class ProjectUpdate(UpdateView):
    model = Project
    fields = ['title', 'end_date']
    template_name_suffix = '_update_form'


class ProjectDelete(DeleteView):
    model = Project
    success_url = reverse_lazy('author-list')
    template_name_suffix = '_delete_form'

