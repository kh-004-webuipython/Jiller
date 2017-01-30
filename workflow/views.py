from django.http import HttpResponseRedirect
from django.shortcuts import get_list_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

from .forms import LoginForm, RegistrationForm, ProjectForm, SprintCreateForm, IssueForm
from .models import Project, ProjectTeam, Issue, Sprint, Employee

from django.utils.decorators import method_decorator
from .decorators import user_belongs_project, \
    edit_project_detail, create_project, create_sprint
from waffle.decorators import waffle_flag
import waffle


def index(request):
    return render(request, 'workflow/index.html')


def profile(request):
    current_user = request.user
    return render(request, 'workflow/profile.html', {
        'user': current_user
    })


class ProjectListView(ListView):
    model = Project
    template_name = 'workflow/projects.html'

    def get_queryset(self):
        return Project.objects.filter(is_active=True).order_by('-start_date')


@user_belongs_project
def sprints_list(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    sprints = Sprint.objects.filter(project=project_id) \
        .exclude(status=Sprint.ACTIVE)

    return render(request, 'workflow/sprints_list.html', {'project': project,
                                                          'sprints': sprints})


@user_belongs_project
@waffle_flag('create_issue', 'workflow:projects')
def create_issue(request, project_id):
    if request.method == "POST":
        form = IssueForm(request.POST)
        if form.is_valid():
            new_issue = form.save(commit=False)
            new_issue.save()
            return redirect('workflow:backlog', project_id)
    else:
        form = IssueForm()
    return render(request, 'workflow/edit_issue.html', {'form': form})


@user_belongs_project
@waffle_flag('edit_issue', 'workflow:projects')
def edit_issue(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id, project=project_id)
    if request.method == "POST":
        form = IssueForm(request.POST, instance=current_issue)
        if form.is_valid():
            current_issue = form.save(commit=False)
            current_issue.save()
            return redirect('workflow:backlog', project_id)
    else:
        form = IssueForm(instance=current_issue)
    return render(request, 'workflow/edit_issue.html', {'form': form})


@user_belongs_project
def team(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    try:
        team_list = ProjectTeam.objects.filter(project=current_project)
    except ProjectTeam.DoesNotExist:
        raise Http404("No team on project")
    return render(request, 'workflow/team.html', {'team_list': team_list,
                                                  'project': current_project})


@user_belongs_project
def backlog(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    issues = Issue.objects.filter(project=project_id) \
        .filter(sprint__isnull=True)

    return render(request, 'workflow/backlog.html', {'project': project,
                                                     'issues': issues})


@user_belongs_project
def issue(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'workflow/issue.html', {
        'issue': current_issue, 'project': project
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

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(SprintView, self).dispatch(*args, **kwargs)


def login_form_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                return redirect('workflow:profile')
            else:
                messages.error(request, _("Wrong username or password"))
                return redirect('workflow:login')
    else:
        form = LoginForm()
    return render(request, 'workflow/login.html', {'form': form})


def registration_form_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            email = form.cleaned_data['email']
            employee = Employee.objects.create_user(username, email, password,
                                                    last_name=last_name,
                                                    first_name=first_name)
            return redirect('workflow:index')
    else:
        form = RegistrationForm()
    return render(request, 'workflow/registration.html', {'form': form})


def user_logout_view(request):
    logout(request)
    return redirect('workflow:login')


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'workflow/project_create_form.html'

    def get_success_url(self):
        return reverse('workflow:project_detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(create_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectDetailView(DetailView):
    model = Project
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'workflow/project_detail.html'

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDetailView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'workflow/project_update_form.html'

    def get_success_url(self):
        return reverse('workflow:project_detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(edit_project_detail)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)


class ProjectDeleteView(DeleteView):
    model = Project

    def get_success_url(self):
        return reverse('workflow:projects')

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])

        project.is_active = False
        project.save()
        return HttpResponseRedirect(
            reverse('workflow:projects'))


def employee_index_view(request):
    employee_list = Employee.objects.all()
    return render(request, 'employee/index.html',
                  {'employee_list': employee_list})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    return render(request, 'employee/detail.html', {'employee': employee})


class SprintCreate(CreateView):
    model = Sprint
    form_class = SprintCreateForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name_suffix = '_create_form'

    def get_context_data(self, **kwargs):
        context = super(SprintCreate, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse('workflow:sprint', args=(self.object.project_id,
                                          self.object.id))

    @method_decorator(create_sprint)
    def dispatch(self, *args, **kwargs):
        return super(SprintCreate, self).dispatch(*args, **kwargs)


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
        context['project'] = Project.objects.get(pk=cur_proj)
        issues_from_this_sprint = Issue.objects.filter(project_id=cur_proj,
                                                       sprint_id=cur_spr)
        context['new_issues'] = issues_from_this_sprint.filter(
            status="new")
        context['in_progress_issues'] = issues_from_this_sprint.filter(
            status="in progress")
        context['resolved_issues'] = issues_from_this_sprint.filter(
            status="resolved")
        # TODO: issue need status closed
        # context['closed'] = issues_from_this_sprint.filter(
        #    status="closed")

        return context

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(SprintView, self).dispatch(*args, **kwargs)


class ActiveSprintView(DetailView):
    model = Sprint
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'workflow/active_sprint.html'

    def get_context_data(self, **kwargs):
        context = super(ActiveSprintView, self).get_context_data(
            **kwargs)

        try:
            Sprint.objects.get(project_id=self.kwargs['project_id'],
                               status='active')
        except Sprint.DoesNotExist:
            context['project'] = Project.objects.get(id=self.kwargs['project_id'])
            context['no_active_sprint'] = True

            return context
        else:

            active_sprint = Sprint.objects.get(project_id=self.kwargs['project_id'],
                                               status='active')
            context['active_sprint'] = active_sprint
            issues_from_active_sprint = Issue.objects.filter(
                project_id=self.kwargs['project_id'], sprint_id=active_sprint.id)
            context['new_issues'] = issues_from_active_sprint.filter(status="new")
            context['in_progress_issues'] = issues_from_active_sprint.filter(
                status="in progress")
            context['resolved_issues'] = issues_from_active_sprint.filter(
                status="resolved")
            context['project'] = Project.objects.get(id=self.kwargs['project_id'])
            return context

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(ActiveSprintView, self).dispatch(*args, **kwargs)


@user_belongs_project
@waffle_flag('push_issue', 'workflow:projects')
def push_issue_in_active_sprint(request, project_id, issue_id, slug):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    sprint = Sprint.objects.get(pk=current_issue.sprint_id)

    if slug == 'right' and sprint and sprint.status != 'new':
        if current_issue.status == "new":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "resolved"
            current_issue.save()
    elif slug == 'left' and sprint and sprint.status != 'finished':
        if current_issue.status == "resolved":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "new"
            current_issue.save()
    return HttpResponseRedirect(
        reverse('workflow:active_sprint', args=(project_id)))

# This view for delete sprint. Hidden until create field is_active in
# Sprint model
#
# class SprintDelete(DeleteView):
#    model = Sprint
#    def delete(self, **kwargs):
#        sprint = Sprint.objects.get(id=self.kwargs['pk'])
#        sprint.is_active = False
#        sprint.save()
#        return HttpResponseRedirect(
#            reverse('workflow:sprints_list'))
