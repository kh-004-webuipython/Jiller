from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView, ListView
from django.urls import reverse

from .forms import ProjectForm, SprintCreateForm, IssueForm
from .models import Project, ProjectTeam, Issue, Sprint


class ProjectListView(ListView):
    model = Project
    template_name = 'workflow/projects.html'

    def get_queryset(self):
        return Project.objects.filter(is_active=True).order_by('-start_date')


def sprints_list(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    sprints = Sprint.objects.filter(project=project_id) \
        .exclude(status=Sprint.ACTIVE)

    return render(request, 'workflow/sprints_list.html', {'project': project,
                                                          'sprints': sprints})


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


def team(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    try:
        team_list = ProjectTeam.objects.filter(project=current_project)
    except ProjectTeam.DoesNotExist:
        raise Http404("No team on project")
    return render(request, 'workflow/team.html', {'team_list': team_list,
                                                  'project': current_project})


def backlog(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    issues = Issue.objects.filter(project=project_id) \
        .filter(sprint__isnull=True)

    return render(request, 'workflow/backlog.html', {'project': project,
                                                     'issues': issues})


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


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'workflow/project_create_form.html'

    def get_success_url(self):
        return reverse('workflow:project_detail',
                       kwargs={'pk': self.object.id})


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'workflow/project_detail.html'


class ProjectUpdateView(UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'workflow/project_update_form.html'

    def get_success_url(self):
        return reverse('workflow:project_detail',
                       kwargs={'pk': self.object.id})


class ProjectDeleteView(DeleteView):
    model = Project

    def get_success_url(self):
        return reverse('workflow:projects')

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['pk'])

        project.is_active = False
        project.save()
        return HttpResponseRedirect(
            reverse('workflow:projects'))


class SprintCreate(CreateView):
    model = Sprint
    form_class = SprintCreateForm
    template_name_suffix = '_create_form'

    def get_context_data(self, **kwargs):
        context = super(SprintCreate, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['pk'])
        return context

    def get_success_url(self):
        return reverse('workflow:sprint', args=(self.object.project_id,
                                          self.object.id))


class ActiveSprintView(DetailView):
    model = Sprint
    template_name = 'workflow/active_sprint.html'

    def get_context_data(self, **kwargs):
        context = super(ActiveSprintView, self).get_context_data(
            **kwargs)

        try:
            Sprint.objects.get(project_id=self.kwargs['pk'],
                               status='active')
        except Sprint.DoesNotExist:
            context['project'] = Project.objects.get(id=self.kwargs['pk'])
            context['no_active_sprint'] = True

            return context
        else:

            active_sprint = Sprint.objects.get(project_id=self.kwargs['pk'],
                                               status='active')
            context['active_sprint'] = active_sprint
            issues_from_active_sprint = Issue.objects.filter(
                project_id=self.kwargs['pk'], sprint_id=active_sprint.id)
            context['new_issues'] = issues_from_active_sprint.filter(status="new")
            context['in_progress_issues'] = issues_from_active_sprint.filter(
                status="in progress")
            context['resolved_issues'] = issues_from_active_sprint.filter(
                status="resolved")
            context['project'] = Project.objects.get(id=self.kwargs['pk'])
            return context


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
