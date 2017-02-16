import datetime
import json

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.http.request import QueryDict
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.utils.decorators import method_decorator
from django.urls import reverse

from django_tables2 import SingleTableView, RequestConfig
from waffle.decorators import waffle_flag

from .forms import ProjectForm, SprintCreateForm, CreateTeamForm, \
    IssueCommentCreateForm, CreateIssueForm, IssueLogForm, \
    IssueFormForEditing, SprintFinishForm
from .models import Project, ProjectTeam, Issue, Sprint, ProjectNote
from .decorators import delete_project, \
    edit_project_detail, create_project, create_sprint
from .tables import ProjectTable, SprintsListTable, IssuesTable,  CurrentTeamTable, AddTeamTable
from django.template.loader import render_to_string
from .utils.workload_manager import put_issue_back_to_pool, \
    calc_work_hours, assign_issue, get_pool

from employee.models import Employee


class ProjectListView(SingleTableView):
    model = Project
    table_class = ProjectTable
    template_name = 'project/projects.html'
    table_pagination = True

    table_pagination = {
        'per_page': settings.PAGINATION_PER_PAGE
    }

    def get_queryset(self):
        projects = Project.objects.get_user_projects(
            self.request.user).order_by(
            '-start_date')
        return projects


def sprints_list(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    sprints = Sprint.objects.filter(project=project_id) \
        .exclude(status=Sprint.ACTIVE)

    table = SprintsListTable(sprints)
    RequestConfig(request,
                  paginate={'per_page': settings.PAGINATION_PER_PAGE}). \
        configure(table)
    return render(request, 'project/sprints_list.html', {'project': project,
                                                         'table': table})


def backlog(request, project_id):
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise Http404("Project does not exist")
    issues = Issue.objects.filter(project=project_id) \
        .filter(sprint__isnull=True).filter(~Q(status='deleted'))

    return render(request, 'project/backlog.html', {'project': project,
                                                    'issues': issues})


@waffle_flag('create_issue', 'project:list')
def issue_create_view(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    form = CreateIssueForm(project=current_project, user=request.user)
    if request.method == "POST":
        form = CreateIssueForm(project=current_project, data=request.POST,
                               user=request.user)
        if form.is_valid():
            new_issue = form.save(commit=False)
            new_issue.project = current_project
            new_issue.author = request.user
            new_issue.save()
            form.send_email(request.user.id, new_issue.id)
            return redirect('project:backlog', current_project.id)
    else:
        initial = {}
        if request.GET.get('root', False):
            initial['root'] = request.GET['root']
            form = CreateIssueForm(project=current_project, initial=initial,
                                   user=request.user)
    return render(request, 'project/issue_create.html', {'form': form,
                                                         'project': current_project})


@waffle_flag('edit_issue', 'project:list')
def issue_edit_view(request, project_id, issue_id):
    current_project = get_object_or_404(Project, pk=project_id)
    current_issue = get_object_or_404(Issue, pk=issue_id,
                                      project=current_project.id)
    if request.method == "POST":
        form = IssueFormForEditing(project=current_project, data=request.POST,
                         instance=current_issue, user=request.user)
        if form.is_valid():
            current_issue = form.save(commit=False)
            current_issue.project = current_project
            current_issue.author = request.user
            current_issue.save()
            form.send_email(request.user.id, current_issue.id)
            return redirect('project:backlog', current_project.id)
    else:
        form = IssueFormForEditing(project=current_project,
                                   instance=current_issue,user=request.user)
    return render(request, 'project/issue_edit.html',
                  {'form': form,
                   'project': current_project,
                   'issue': Issue.objects.get(pk=current_issue.id)})


def team_view(request, project_id):
    data = {}
    current_project = get_object_or_404(Project, pk=project_id)
    data.update({'project': current_project})

    # filter needs for possibility to add two PMs, when we need change 1st PM
    project_managers = Employee.objects.filter(projectteam__project=project_id,
                                               groups__name='project manager')
    data.update({'pm': project_managers})

    # for one project it could be only one team
    team = get_object_or_404(ProjectTeam, project_id=current_project)
    data.update({'team': team})
    e_list = []
    if team.employees.count() != 1:
        for employee in team.employees.all():
            if employee not in project_managers:
                e_list.append({'id_team': team.id, 'id': employee.id,
                               'project': team.project, 'title': team.title,
                               'get_full_name': employee.get_full_name(),
                               'role': employee.groups})

        table_cur = CurrentTeamTable(e_list)
        data.update({'table_cur': table_cur})
        RequestConfig(request, paginate={'per_page': settings.PAGINATION_PER_PAGE}).\
                                         configure(table_cur)


    # hide PMs on "global" team board
    u_list = []
    user_list = 'None'

    if request.user.groups.filter(name='project manager').exists():
        user_list = Employee.objects.exclude(groups__name='project manager').\
                                     exclude(projectteam__project=project_id)
                                     #exclude(groups__name='product owner')
        for user in user_list:
            u_list.append({'id': user.id, 'get_full_name': user.get_full_name(),
                           'role': user.groups})

        table_add = AddTeamTable(u_list)
        data.update({'table_add': table_add})
        RequestConfig(request, paginate={'per_page': settings.PAGINATION_PER_PAGE}).\
                                         configure(table_add)
    else:
        table_cur = CurrentTeamTable(e_list)
        table_cur.exclude = ('sub')

    return render(request, 'project/team.html', data)


def issue_detail_view(request, project_id, issue_id):
    current_issue = get_object_or_404(Issue, pk=issue_id)
    project = get_object_or_404(Project, pk=project_id)

    if request.method == 'POST':
        if 'comment' in request.POST:
            form = IssueCommentCreateForm(request.POST)
            if form.is_valid():
                comment = form.save(commit=False)
                comment.author = request.user
                comment.issue = current_issue
                comment.save()
                return redirect(reverse('project:issue_detail',
                                        args=(project.id, current_issue.id)))

        if 'log' in request.POST:
            form = IssueLogForm(request.POST, issue=current_issue)
            if form.is_valid():
                log = form.save(commit=False)
                log.issue = current_issue
                log.user = request.user
                log.save()
                return JsonResponse({'success': True, 'errors': None}, status=201)
            return JsonResponse({'success': False, 'error': form.errors}, status=400)

    if current_issue.project_id != project.id:
        raise Http404("Issue does not exist")
    context = {
        'issue': current_issue, 'project': project
    }
    if current_issue.root:
        context['root_issue'] = Issue.objects.get(pk=current_issue.root.id)
    child_issues = Issue.objects.filter(root=current_issue.id)
    if child_issues:
        context['child_issues'] = child_issues
    context['comment_form'] = IssueCommentCreateForm()
    context['log_form'] = IssueLogForm()
    return render(request, 'project/issue_detail.html', context)


class IssueDeleteView(DeleteView):
    model = Issue
    query_pk_and_slug = True
    pk_url_kwarg = 'issue_id'

    def get_success_url(self):
        return reverse('project:backlog',
                       kwargs={'project_id': self.object.project_id})

    def get_context_data(self, **kwargs):
        context = super(IssueDeleteView, self).get_context_data(**kwargs)
        currrent_project = self.kwargs['project_id']
        current_issue = self.kwargs['issue_id']
        context['project'] = Project.objects.get(id=currrent_project)
        context['issue'] = Issue.objects.get(id=current_issue)
        return context

    def delete(self, request, *args, **kwargs):
        project = Project.objects.get(id=kwargs['project_id'])
        issue = Issue.objects.get(id=kwargs['issue_id'])
        issue.status = 'deleted'
        issue.save()
        return HttpResponseRedirect(reverse('project:backlog',
                                            kwargs={'project_id': project.id}))


class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    query_pk_and_slug = True
    pk_url_kwarg = 'project_id'
    template_name = 'project/project_create_form.html'

    def form_valid(self, form, *args, **kwargs):
        project = form.save(commit=False)
        project.save()
        if not ProjectTeam.objects.filter(project=project):
            team = ProjectTeam.objects.create(project=project,
                                              title=project.title)
            team.employees.add(self.request.user)
        return super(ProjectCreateView, self).form_valid(form, *args, **kwargs)

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

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SprintCreate, self).get_form_kwargs()
        kwargs.pop('instance', None)
        kwargs['project'] = self.project
        return kwargs

    def get_initial(self):
        return {'status': Sprint.NEW}

    def form_valid(self, form):
        sprint = form.save(commit=False)
        sprint.project = self.project
        sprint.start_date = datetime.datetime.now()
        sprint.save()
        issue = form.cleaned_data['issue']
        issue.update(sprint=sprint)
        self.object = sprint
        return redirect(
            reverse('project:sprint_active', args=(self.object.project.id,)))

    def get_context_data(self, **kwargs):
        project = Project.objects.get(id=self.kwargs['project_id'])
        context = super(SprintCreate, self).get_context_data(**kwargs)
        context['project'] = self.project
        context['issue_list'] = project.issue_set.filter(sprint=None).order_by(
            'order')
        return context

    def get_success_url(self):
        return reverse('project:sprint_detail', args=(self.object.project.id,
                                                      self.object.id))

    @method_decorator(create_sprint)
    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return super(SprintCreate, self).dispatch(*args, **kwargs)


class SprintView(DeleteView):
    model = Sprint
    template_name = 'project/sprint_detail.html'

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['sprint_id'])

    def dispatch(self, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return super(SprintView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SprintView, self).get_context_data(**kwargs)
        if self.object:
            issues_from_this_sprint = self.object.issue_set.all()
            context['new_issues'] = issues_from_this_sprint.filter(status="new")
            context['in_progress_issues'] = \
                issues_from_this_sprint.filter(status="in progress")
            context['resolved_issues'] = \
                issues_from_this_sprint.filter(status="resolved")
            context['closed_issues'] = issues_from_this_sprint.filter(
                status="closed")
            context['chart'] = self.object.chart()
            context['form'] = SprintFinishForm()
        context['project'] = self.project
        return context


class ActiveSprintDetailView(SprintView):
    template_name = 'project/sprint_active.html'
    context_object_name = 'active_sprint'

    def get_object(self, queryset=None):
        return self.project.sprint_set.filter(status=Sprint.ACTIVE).first()


@waffle_flag('push_issue', 'project:list')
def push_issue_in_active_sprint(request):
    if request.method == 'POST':
        if 'table' in request.POST and 'id' in request.POST:
            table = str(request.POST.get('table', None))
            row = int(request.POST.get('id', None))
            current_issue = get_object_or_404(Issue, pk=row)
            sprint = get_object_or_404(Sprint, pk=current_issue.sprint_id)
            if sprint.status == Sprint.ACTIVE and table in [Issue.IN_PROGRESS,
                                                            Issue.NEW,
                                                            Issue.RESOLVED]:
                current_issue.status = table
                current_issue.save()
                return HttpResponse()
            raise Http404("Wrong request")
    else:
        raise Http404("Wrong request")


class IssueSearchView(SingleTableView):
    model = Issue
    table_class = IssuesTable
    template_name = 'project/issues_search.html'
    table_pagination = {
        'per_page': settings.PAGINATION_PER_PAGE
    }

    def get_queryset(self):
        status = self.request.GET.get('status', None)
        type = self.request.GET.get('type', None)
        search_string = self.request.GET.get('s', None)
        query_expr = Issue.objects.filter(project_id=self.kwargs['project_id'])
        if type:
            query_expr = query_expr.filter(type=type)  # Not Implemented
        if status and status!='all':
            query_expr = query_expr.filter(status=status)
        if search_string:
            query_expr = query_expr.filter(Q(title__contains=search_string) | Q(description__contains=search_string))
        return query_expr

    def get_context_data(self, **kwargs):
        context = super(IssueSearchView, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        context['issues_status'] = Issue.ISSUE_STATUS_CHOICES
        return context


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


@waffle_flag('prioritize_issue', 'project:detail')
def issue_order(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        keys = data.keys()

        if data:
            for key in keys:
                try:
                    issue = Issue.objects.get(id=int(key))
                except Issue.DoesNotExist:
                    raise Http404("Issue does not exist")
                issue.order = int(data[key])
                issue.save()
        return HttpResponse()
    else:
        return HttpResponseRedirect(reverse('project:list'))


def change_user_in_team(request, project_id, user_id, team_id):
    if request.method == 'POST':
        user = Employee.objects.get(pk=user_id)
        if 'add' in request.POST:
            team = get_object_or_404(ProjectTeam, pk=team_id)
            team.employees.add(user)
        if 'remove' in request.POST:
            team = get_object_or_404(ProjectTeam, pk=team_id)
            team.employees.remove(user)
        return redirect('project:team', project_id)
    return redirect('project:team', project_id)


def team_create(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = CreateTeamForm(request.POST)
        if form.is_valid():
            new_team = form.save(commit=False)
            new_team.project = project
            new_team.save()
            new_team.employees.add(request.user.id)
            return redirect('project:team', project_id)
    else:
        form = CreateTeamForm()
    return render(request, 'project/team_create.html', {'form': form,
                                                        'project': project})


@waffle_flag('read_workflow_manager', 'project:list')
def workload_manager(request, project_id, sprint_status):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))

        employee_id = data['employee']
        issue = Issue.objects.get(pk=data['issue'])
        # if issue was drugged into pool
        if employee_id == 0:
            put_issue_back_to_pool(project_id, issue, sprint_status)
        else:
            assign_issue(project_id, employee_id, issue, sprint_status)
        issue.save()

    project = get_object_or_404(Project, pk=project_id)
    issues_log = get_pool(project_id, sprint_status)

    try:
        employees = ProjectTeam.objects.filter(project=project)[0]\
            .employees.filter(groups__pk__in=[1, 2])
    except ProjectTeam.DoesNotExist:
        raise Http404("ProjectTeam does not exist")

    items = []
    for employee in employees:
        issues = Issue.objects.filter(project=project_id) \
            .filter(sprint__status=sprint_status, employee=employee).filter(~Q(status='deleted'))
        items.append({'employee': employee, 'issues': issues})

    try:
        sprint = Sprint.objects.get(project=project_id, status=sprint_status)
    except Sprint.DoesNotExist:
        raise Http404("Sprint does not exist")

    work_hours = calc_work_hours(sprint)
    for item in items:
        sum = 0
        for issue in item['issues']:
            if not issue.estimation:
                return HttpResponse('The issue has to be estimated', status=401)
            sum += issue.estimation

        item['workload'] = sum * 100 / work_hours
        item['free'] = work_hours - sum

    context = {'items': items,
               'project': project,
               'issues_log': issues_log,
               'sprint_status': sprint_status}

    if request.is_ajax():
        html = render_to_string('project/workload_template.html', context)
        return HttpResponse(html)

    return render(request, 'project/workload_manager.html', context)


@waffle_flag('only_developer')
def notes_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "GET":
        notes = ProjectNote.objects.filter(project_id=project_id)
        return render(request, 'project/notes.html', {'project': project,
                                                      'notes': notes})
    if request.method == "POST":
        if 'id' in request.POST and 'title' in request.POST and 'content' \
                in request.POST:
            id = request.POST.get('id', None)
            title = str(request.POST.get('title', None))
            content = str(request.POST.get('content', None))
            if id == 'undefined' and len(content) <= 5000 and len(title) <= 15:
                note = ProjectNote.objects.create(project_id=project.id)
                note.title = title
                note.content = content
                note.save()
                response = HttpResponse()
                response.__setitem__('note_id', str(note.id))
                return response
            else:
                note = get_object_or_404(ProjectNote, pk=int(id))
                if len(content) <= 5000 and len(title) <= 15:
                    note.title = title
                    note.content = content
                    note.save()
                    return HttpResponse()
            raise Http404("Wrong request")
    if request.method == "DELETE":
        delete = QueryDict(request.body)
        if 'id' in delete:
            id = int(delete.get('id', None))
            note = get_object_or_404(ProjectNote, pk=id)
            note.delete()
            return HttpResponse()
        raise Http404("Wrong request")
    return redirect(request, 'project:notes', {'project': project})


@waffle_flag('edit_sprint')
def finish_active_sprint_view(request, project_id):
    if request.method == "POST":
        active_sprint = get_object_or_404(Sprint, project_id=project_id,
                                          status=Sprint.ACTIVE)
        form = SprintFinishForm(request.POST)
        if form.is_valid():
            relies = form.cleaned_data['relies_link']
            feedback = form.cleaned_data['feedback_text']
            active_sprint.relies_link = relies
            active_sprint.feedback_text = feedback
            active_sprint.status = Sprint.FINISHED
            active_sprint.end_date = datetime.datetime.now()
            active_sprint.save()
            return HttpResponseRedirect(reverse('project:sprint_active',
                                            kwargs={'project_id': project_id}))
    raise Http404
