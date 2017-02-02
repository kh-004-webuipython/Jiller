import datetime

from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

from .forms import ProjectForm, SprintCreateForm, CreateIssueForm, \
    EditIssueForm
from .models import Project, ProjectTeam, Issue, Sprint

from django.utils.decorators import method_decorator
from .decorators import delete_project, user_belongs_project, \
    edit_project_detail, create_project, create_sprint
from waffle.decorators import waffle_flag


class ProjectListView(ListView):
    model = Project
    template_name = 'project/projects.html'

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

    return render(request, 'project/sprints_list.html', {'project': project,
                                                         'sprints': sprints})


@user_belongs_project
@waffle_flag('create_issue', 'project:list')
def issue_create_view(request, project_id):
    if request.method == "POST":
        form = CreateIssueForm(request.POST)
        if form.is_valid():
            new_issue = form.save(commit=False)
            new_issue.save()
            return redirect('project:backlog', project_id)
    else:
        form = CreateIssueForm(
            initial={'project': project_id, 'author': request.user.id})
    return render(request, 'project/create_issue.html', {'form': form,
                                                         'project': Project.objects.get(
                                                             pk=project_id)})


@user_belongs_project
@waffle_flag('edit_issue', 'project:list')
def issue_edit_view(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id, project=project_id)
    if request.method == "POST":
        form = EditIssueForm(request.POST, instance=current_issue)
        if form.is_valid():
            current_issue = form.save(commit=False)
            current_issue.save()
            return redirect('project:backlog', project_id)
    else:
        form = EditIssueForm(instance=current_issue)
    return render(request, 'project/edit_issue.html',
                  {'form': form, 'project': Project.objects.get(pk=project_id),
                   'issue': Issue.objects.get(pk=issue_id)})


@user_belongs_project
def team_view(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    try:
        team_list = ProjectTeam.objects.filter(project=current_project)
    except ProjectTeam.DoesNotExist:
        raise Http404("No team on project")
    return render(request, 'project/team.html', {'team_list': team_list,
                                                 'project': current_project})


@user_belongs_project
def backlog(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    issues = Issue.objects.filter(project=project_id) \
        .filter(sprint__isnull=True)

    return render(request, 'project/backlog.html', {'project': project,
                                                    'issues': issues})


@user_belongs_project
def issue(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    project = get_object_or_404(Project, pk=project_id)
    if current_issue.project_id != project.id:
        raise Http404("Issue does not exist")
    return render(request, 'project/issue_detail.html', {
        'issue': current_issue, 'project': project
    })


class SprintView(DetailView):
    model = Sprint
    template_name = 'project/sprint_detail.html'
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
        context['project'] = Project.objects.get(id=cur_proj)
        return context

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(SprintView, self).dispatch(*args, **kwargs)


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_create_form.html'

    def get_success_url(self):
        return reverse('project:detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(create_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectCreateView, self).dispatch(*args, **kwargs)


class ProjectDetailView(DetailView):
    model = Project
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_detail.html'

    @method_decorator(user_belongs_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDetailView, self).dispatch(*args, **kwargs)


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_update_form.html'

    def get_success_url(self):
        return reverse('project:detail',
                       kwargs={'project_id': self.object.id})

    @method_decorator(edit_project_detail)
    def dispatch(self, *args, **kwargs):
        return super(ProjectUpdateView, self).dispatch(*args, **kwargs)


class ProjectDeleteView(DeleteView):
    model = Project
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'

    def get_success_url(self):
        return reverse('project:list')

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])

        project.is_active = False
        project.save()
        return HttpResponseRedirect(
            reverse('project:list'))

    @method_decorator(delete_project)
    def dispatch(self, *args, **kwargs):
        return super(ProjectDeleteView, self).dispatch(*args, **kwargs)


class SprintCreate(CreateView):
    model = Sprint
    form_class = SprintCreateForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name_suffix = '_create_form'

    def get_initial(self):
        return {
            'project': self.kwargs['project_id'],
            'start_date': datetime.datetime.now(),
            'status': Sprint.NEW
        }

    def get_context_data(self, **kwargs):
        context = super(SprintCreate, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self):
        return reverse('project:sprint_detail', args=(self.object.project_id,
                                                      self.object.id))

    @method_decorator(create_sprint)
    def dispatch(self, *args, **kwargs):
        return super(SprintCreate, self).dispatch(*args, **kwargs)


class ActiveSprintView(DetailView):
    model = Sprint
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/sprint_active.html'

    def get_object(self, queryset=None):
        try:
            return super(ActiveSprintView, self).get_object(queryset)
        except:
            try:
                Project.objects.get(pk=self.kwargs['project_id'])
            except:
                raise Http404("Project does not exist")
        else:
            return None

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
@waffle_flag('push_issue', 'project:list')
def push_issue_in_active_sprint(request, project_id, issue_id, slug):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    sprint = get_object_or_404(Sprint, pk=current_issue.sprint_id)

    if slug == 'right' and sprint.status == 'active':
        if current_issue.status == "new":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "resolved"
            current_issue.save()
    elif slug == 'left' and sprint.status == 'active':
        if current_issue.status == "resolved":
            current_issue.status = "in progress"
            current_issue.save()
        elif current_issue.status == "in progress":
            current_issue.status = "new"
            current_issue.save()
    return HttpResponseRedirect(reverse('project:sprint_active',
                                        args=(project_id)))


class SprintStatusUpdate(UpdateView):
    model = Sprint
    template_name = 'project/sprint_update_form.html'
    pk_url_kwarg = 'sprint_id'
    slug_field = 'project'
    slug_url_kwarg = 'project_id'
    fields = ['status']

    def get_context_data(self, **kwargs):
        context = super(SprintStatusUpdate, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        return context

    def get_success_url(self, **kwargs):
        return reverse('project:sprint_active',
                       kwargs={'project_id': self.object.project_id})


"""
class SprintDelete(DeleteView):
    model = Sprint

    def delete(self, **kwargs):
        sprint = Sprint.objects.get(id=self.kwargs['pk'])
        sprint.is_active = False
        sprint.save()
        return HttpResponseRedirect(
            reverse('project:sprints_list'))
"""
