import datetime
import json
import re

import requests
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponseRedirect, Http404, HttpResponse, \
    HttpResponseBadRequest
from django.http.request import QueryDict
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, \
    render_to_response
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django_tables2 import SingleTableView, RequestConfig
from django.core import serializers
from django.forms.models import model_to_dict
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from waffle.decorators import waffle_flag

from api.serializers import IssueDetailSerializer
from api.views import IssueDetailAPIView
from .forms import ProjectForm, SprintCreateForm, CreateTeamForm, \
    IssueCommentCreateForm, CreateIssueForm, IssueLogForm, \
    IssueFormForEditing, SprintFinishForm, NoteForm, \
    NoteFormWithImage, IssueFormForSprint
from .models import Project, ProjectTeam, Issue, Sprint, ProjectNote
from .decorators import delete_project, \
    edit_project_detail, create_project, create_sprint
from .tables import ProjectTable, SprintsListTable, IssuesTable, \
    ProjectTeamTable
from .utils.workload_manager import put_issue_back_to_pool, \
    calc_work_hours, assign_issue, get_pool
from .utils.user_variator import check_if_issue_assigned, \
    check_issue_add_to_sprint

from employee.models import Employee

from general.tasks import send_email_after_sprint_start_task, \
    send_email_after_sprint_finish_task


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
        .exclude(status__in=[Sprint.ACTIVE, Sprint.NEW])

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
        .filter(sprint__isnull=True).filter(~Q(status='deleted')).filter(
        ~Q(status='closed'))

    return render(request, 'project/backlog.html', {'project': project,
                                                    'issues': issues})


@waffle_flag('create_issue', 'project:list')
def issue_create_view(request, project_id):
    current_project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = CreateIssueForm(project=current_project, data=request.POST,
                               user=request.user)
        if form.is_valid():
            new_issue = form.save(commit=False)
            new_issue.project = current_project
            new_issue.author = request.user
            if request.user.groups.filter(id=3):
                new_issue.estimation = 0
            if check_if_issue_assigned(form):
                new_issue.employee = request.user
            if check_issue_add_to_sprint(form):
                new_issue.sprint = Sprint.objects.get(project=project_id,
                                                      status=Sprint.NEW)
            new_issue.save()
            if check_if_issue_assigned(form):
                form.send_email(request.META['HTTP_HOST'], request.user.id,
                                new_issue.id)
            return redirect('project:backlog', current_project.id)
    else:
        initial = {}
        if request.GET.get('root', False):
            initial['root'] = request.GET['root']
        form = CreateIssueForm(project=current_project, initial=initial,
                               user=request.user)
    return render(request, 'project/issue_create.html',
                  {'form': form, 'project': current_project})


@waffle_flag('edit_issue', 'project:list')
def issue_edit_view(request, project_id, issue_id):
    current_project = get_object_or_404(Project, pk=project_id)
    current_issue = get_object_or_404(Issue, pk=issue_id,
                                      project=current_project.id)
    if request.method == "POST":
        form = IssueFormForEditing(project=current_project, data=request.POST,
                                   instance=current_issue, user=request.user)
        if form.is_valid() and form.changed_data:
            current_issue = form.save()
            form.send_email(request.META['HTTP_HOST'], request.user.id,
                            current_issue.id)

        return redirect('project:issue_detail', current_project.id,
                        current_issue.id)
    else:
        form = IssueFormForEditing(project=current_project,
                                   instance=current_issue, user=request.user)
    return render(request, 'project/issue_edit.html',
                  {'form': form,
                   'project': current_project,
                   'issue': Issue.objects.get(pk=current_issue.id)})


@csrf_protect
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

    row_attrs_data = {'data-pr_id': project_id,
                      'data-id': lambda record: record.pk,
                      'data-team_id': team.pk,
                      'draggable': 'True'}

    table_attrs_data = {"class": "table table-bordered table-striped "
                                 "table-hover table-sm"}

    employee = Employee.objects.filter(projectteam__project=project_id). \
        exclude(groups__name='project manager')

    table_attrs_data.update({"data-table": "table_cur"})
    table_cur = ProjectTeamTable(employee, prefix='1-',
                                 row_attrs=row_attrs_data,
                                 attrs=table_attrs_data)

    table_cur.base_columns['get_full_name'].verbose_name = 'Current employees'

    data.update({'table_cur': table_cur})
    RequestConfig(request,
                  paginate={'per_page': settings.PAGINATION_PER_PAGE}). \
        configure(table_cur)

    # hide PMs on "global" team board
    if request.user.groups.filter(name='project manager').exists():
        user_list = Employee.objects.exclude(groups__name='project manager'). \
            exclude(projectteam__project=project_id)

        table_attrs_data.update({"data-table": "table_add"})
        table_add = ProjectTeamTable(user_list, prefix='2-',
                                     row_attrs=row_attrs_data,
                                     attrs=table_attrs_data)
        table_add.base_columns['get_full_name'].verbose_name = 'Free employees'

        data.update({'table_add': table_add})
        RequestConfig(request,
                      paginate={'per_page': settings.PAGINATION_PER_PAGE}). \
            configure(table_add)

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
                return JsonResponse({'success': True, 'errors': None,
                                     'completion_rate': current_issue.completion_rate(),
                                     'cost': log.cost,
                                     'user': log.user.get_full_name(),
                                     'date_created': log.get_pretty_date_created(),
                                     'user-link': reverse('employee:detail',
                                                          args=[log.user.id]),
                                     'note': log.note},
                                    status=201)
            return JsonResponse({'success': False, 'error': form.errors},
                                status=400)

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
            context['new_issues'] = issues_from_this_sprint.filter(
                status="new")
            context['in_progress_issues'] = \
                issues_from_this_sprint.filter(status="in progress")
            context['resolved_issues'] = \
                issues_from_this_sprint.filter(status="resolved")
            context['closed_issues'] = issues_from_this_sprint.filter(
                status="closed")
            context['chart'] = self.object.chart()
            context['form'] = SprintFinishForm()
        context['create_sprint_form'] = SprintCreateForm()
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
            table = str(request.POST.get('table'))
            row = int(request.POST.get('id'))
            current_issue = get_object_or_404(Issue, pk=row)
            sprint = get_object_or_404(Sprint, pk=current_issue.sprint_id)
            if sprint.status == Sprint.ACTIVE and table in [Issue.IN_PROGRESS,
                                                            Issue.NEW,
                                                            Issue.RESOLVED]:
                current_issue.status = table
                current_issue.save()
                return HttpResponseRedirect(reverse('project:sprint_active',
                                                    kwargs={
                                                        'project_id': sprint.project_id}))
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
        status = self.request.GET.getlist('status', None)
        issue_type = self.request.GET.getlist('type', None)
        search_string = self.request.GET.get('s', None)
        estimation_from = self.request.GET.get('estimation_from', None)
        estimation_to = self.request.GET.get('estimation_to', None)
        query_expr = Issue.objects.filter(project_id=self.kwargs['project_id'])
        if issue_type:
            query_expr = query_expr.filter(type__in=issue_type)
        if status and status != 'all':
            query_expr = query_expr.filter(status__in=status)
        if estimation_to:
            query_expr = query_expr.filter(estimation__lte=estimation_to)
        if estimation_from:
            query_expr = query_expr.filter(estimation__gte=estimation_from)
        if search_string:
            query_expr = query_expr.filter(
                Q(title__icontains=search_string) | Q(
                    description__icontains=search_string))
        return query_expr

    def get_context_data(self, **kwargs):
        context = super(IssueSearchView, self).get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=self.kwargs['project_id'])
        context['issues_status'] = Issue.ISSUE_STATUS_CHOICES
        context['issue_types'] = Issue.ISSUE_TYPE_CHOICES
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


@waffle_flag('read_workflow_manager', 'project:list')
def workload_manager(request, project_id, sprint_status):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))

        relate = data['relate']
        issue = Issue.objects.get(pk=data['issue'])
        # if issue was drugged into backlog or sprint pool
        error = None
        if relate in ['backlog', 'new_sprint', 'active_sprint']:
            error = put_issue_back_to_pool(request, project_id, issue, relate)
        else:
            error = assign_issue(project_id, relate, issue, sprint_status)
        if error:
            return error
        issue.save()

    project = get_object_or_404(Project, pk=project_id)
    issues_log = get_pool(project_id, 'backlog')
    sprint_log = get_pool(project_id, sprint_status)

    try:
        employees = ProjectTeam.objects.get(project=project) \
            .employees.filter(groups__pk__in=[1, 2])
    except ProjectTeam.DoesNotExist:
        raise Http404("ProjectTeam does not exist")

    items = []
    for employee in employees:
        issues = Issue.objects.filter(project=project_id) \
            .filter(sprint__status=sprint_status, employee=employee) \
            .exclude(status=Issue.DELETED)
        items.append({'employee': employee, 'issues': issues, 'resolved': []})

    try:
        sprint = Sprint.objects.get(project=project_id, status=sprint_status)
    except Sprint.DoesNotExist:
        raise Http404("Sprint does not exist")

    work_hours = int(calc_work_hours(sprint))
    for item in items:
        totalEstim = sum((issue.estimation for issue in item['issues']))
        item['resolved'] = [issue for issue in item['issues'] if
                            issue.status == Issue.RESOLVED]

        item['workload'] = totalEstim * 100 / work_hours
        item['free'] = work_hours - totalEstim

    form = IssueFormForSprint(project=project, initial={}, user=request.user)
    context = {'items': items,
               'project': project,
               'issues_log': issues_log,
               'sprint_status': sprint_status,
               'sprint_log': sprint_log,
               'form': form}

    if request.is_ajax():
        html = render(request, 'project/workload_template.html', context)
        return HttpResponse(html)

    return render(request, 'project/workload_manager.html', context)


def notes_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "GET":
        notes = ProjectNote.objects.filter(project_id=project_id)
        max_len = {}
        max_len['t'] = ProjectNote._meta.get_field('title').max_length
        max_len['c'] = ProjectNote._meta.get_field('content').max_length
        return render(request, 'project/notes.html', {'project': project,
                                                      'notes': notes,
                                                      'max': max_len})

    if request.method == "POST" and 'id' in request.POST:
        id_val = request.POST.get('id')

        if id_val == 'undefined':
            if request.FILES:
                form = NoteFormWithImage(request.POST, request.FILES)
                if form.is_valid():
                    note = form.save(commit=False)
                    note.project_id = project_id
                    note.picture = request.FILES['picture']
                    note.save()
                    response = HttpResponse()
                    response.__setitem__('newImg',
                                         settings.MEDIA_URL + str(
                                             note.picture))
                    response.__setitem__('note_id', str(note.id))
                    return response
            else:
                form = NoteForm(request.POST)
                if form.is_valid():
                    note = form.save(commit=False)
                    note.project_id = project_id
                    note.save()
                    response = HttpResponse()
                    response.__setitem__('note_id', str(note.id))
                    return response
                return HttpResponseBadRequest()
        elif request.FILES:
            note = get_object_or_404(ProjectNote, pk=int(id_val))
            form = NoteFormWithImage(request.POST, request.FILES)
            if form.is_valid():
                note.picture = request.FILES['picture']
                note.save()
                response = HttpResponse()
                response.__setitem__('newImg',
                                     settings.MEDIA_URL + str(note.picture))
                return response
            response = HttpResponseBadRequest()
            response.__setitem__('errorForm',
                                 'This picture does not fit ' +
                                 'the specified parameters')
            return response

        else:
            note = get_object_or_404(ProjectNote, pk=int(id_val))
            old_title = request.POST.get('oldTitle')
            old_content = request.POST.get('oldContent')
            if re.sub("^\s+|\n|\r|\s+$", '', note.content) != \
                    re.sub("^\s+|\n|\r|\s+$", '', old_content) or \
                            note.title != old_title:
                response = HttpResponseBadRequest()
                response.__setitem__('error', 'Oops, someone has updated ' +
                                     'this note before you, please refresh ' +
                                     'page and then write new changes!')
                return response
            form = NoteForm(request.POST, instance=note)
            if form.is_valid():
                form.save()
                return HttpResponse()
            response = HttpResponseBadRequest()
            input_c_length = ProjectNote._meta.get_field('content').max_length
            if len(request.POST.get('content')) >= input_c_length:
                response.__setitem__('error',
                                     'You have typed to limit in 10000 chars!')
                return response
    if request.method == "DELETE":
        delete = QueryDict(request.body)
        if 'id' in delete:
            id_val = int(delete.get('id'))
            note = get_object_or_404(ProjectNote, pk=id_val)
            note.delete()
            return HttpResponse()
        raise Http404("Wrong request")
    return HttpResponseBadRequest()


@waffle_flag('edit_sprint')
def finish_active_sprint_view(request, project_id):
    if request.method == "POST":
        active_sprint = get_object_or_404(Sprint, project_id=project_id,
                                          status=Sprint.ACTIVE)
        form = SprintFinishForm(request.POST)
        if form.is_valid():

            user_id = request.user.id
            sprint_id = active_sprint.id
            employees = ProjectTeam.objects.get(
                project_id=project_id).employees.all()

            active_sprint.release_link = form.cleaned_data['release_link']
            active_sprint.feedback_text = form.cleaned_data['feedback_text']
            active_sprint.status = Sprint.FINISHED
            active_sprint.end_date = datetime.datetime.now()
            active_sprint.save()
            for member in employees:
                send_email_after_sprint_finish_task.delay(
                    request.META['HTTP_HOST'],
                    member.email,
                    user_id,
                    sprint_id,
                    active_sprint.release_link,
                    active_sprint.feedback_text)
            return HttpResponseRedirect(reverse('project:sprint_active',
                                                kwargs={
                                                    'project_id': project_id}))
    raise Http404("Wrong request")


@waffle_flag('create_sprint')
def sprint_create_view(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        form = SprintCreateForm(request.POST)

        if form.is_valid():
            new_sprint = form.save(commit=False)
            new_sprint.project = project
            new_sprint.status = Sprint.NEW
            new_sprint.save()
            return HttpResponseRedirect(reverse('project:workload_manager',
                                                args=[project_id, Sprint.NEW]))
    raise Http404


@waffle_flag('edit_sprint')
def sprint_start_view(request, project_id):
    if request.method == "POST":
        current_sprint = get_object_or_404(Sprint, project_id=project_id,
                                           status=Sprint.NEW)
        current_sprint.status = Sprint.ACTIVE
        current_sprint.start_date = datetime.datetime.now()
        try:
            current_sprint.save()
        except ValidationError:
            message = 'to start sprint you need to finish active one'
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('project:sprint_active',
                                                args=[project_id, ]))
        else:
            user_id = request.user.id
            sprint_id = current_sprint.id
            employees = ProjectTeam.objects.get(
                project_id=project_id).employees.all()
            for member in employees:
                send_email_after_sprint_start_task.delay(
                    request.META['HTTP_HOST'], member.email, user_id,
                    sprint_id)
        return HttpResponseRedirect(reverse('project:sprint_active',
                                            args=[project_id, ]))
    raise Http404


@waffle_flag('create_task', 'project:list')
def issue_create_workload(request, project_id, sprint_status):
    if request.method == "POST":
        project = get_object_or_404(Project, pk=project_id)
        form = IssueFormForSprint(project=project, data=request.POST,
                                  user=request.user)
        if form.is_valid():
            sprint = get_object_or_404(Sprint, project_id=project_id,
                                       status=sprint_status)
            current_issue = form.save(commit=False)
            current_issue.project = project
            current_issue.sprint = sprint
            current_issue.author = request.user
            if check_if_issue_assigned(form):
                current_issue.employee = request.user
            current_issue.save()
            return HttpResponseRedirect(reverse('project:workload_manager',
                                                args=[project_id,
                                                      sprint_status]))
    raise Http404


def poker_room_redirect_view(request, project_id):
    host = 'http://' + request.META['HTTP_HOST'].split(':')[0] + ':5000/'
    link = host + 'room/' + str(project_id) + '/user/'+ str(request.user.id)
    return redirect(link)


def create_poker_room_view(request, project_id):
    host = 'http://' + request.META['HTTP_HOST'].split(':')[0] + ':5000/'
    project = Project.objects.get(id=project_id)
    team = ProjectTeam.objects.get(project=project.id)
    url = host + 'create_room/'
    team_list = []
    for employee in team.employees.all():
        employee_dict = {'id': employee.id, 'name': employee.username}
        team_list.append(employee_dict)
    data = {'project_id': project.id, 'title': project.title, 'team': team_list}
    headers = {'Content-Type': 'application/json'}

    r = requests.post(url, data=json.dumps(data), headers=headers)

    return redirect('project:issue_search', int(project_id))


def poker_room_with_issue_redirect_view(request, project_id, issue_id):
    host = 'http://' + request.META['HTTP_HOST'].split(':')[0] + ':5000/'
    project = Project.objects.get(id=project_id)
    issue = Issue.objects.get(id=issue_id)
    url = host + 'add_issue/'
    data_list = []
    data = model_to_dict(issue, fields=['id', 'title', 'description'])

    data.update({'project_id': project.id, 'estimation': ''})
    data_list.append(data)
    headers = {'Content-Type': 'application/json',
               'user_id': str(request.user.id)}

    r = requests.post(url, data=json.dumps(data_list), headers=headers)

    return HttpResponseRedirect(host + 'room/' + str(project.id) + '/user/' +
                                str(request.user.id))


def poker_room_with_sprint_redirect_view(request, project_id):
    host = 'http://' + request.META['HTTP_HOST'].split(':')[0] + ':5000/'
    project = Project.objects.get(id=project_id)
    issue_sprint = Sprint.objects.get(status=Sprint.NEW)
    issues = Issue.objects.filter(sprint=issue_sprint)
    url = host + 'add_issue/'
    data_list = []
    for issue in issues:
        data = model_to_dict(issue, fields=['id', 'title', 'description'])
        data.update({'project_id': project.id, 'estimation': ''})
        data_list.append(data)

    headers = {'Content-Type': 'application/json'}

    r = requests.post(url, data=json.dumps(data_list), headers=headers)

    return HttpResponseRedirect(host + 'room/' + str(project.id) + '/user/' +
                                str(request.user.id))


@csrf_exempt
def save_issue_estimation_view(request, project_id, issue_id):
    if request.method == "POST":

        current_project= get_object_or_404(Project, id=project_id)
        current_issue = get_object_or_404(Issue, id=issue_id)
        current_issue.estimation = int(request.POST['estimation'])
        try:
            current_issue.save()
        except ValidationError:
            message = 'estimation is incorrect'
            messages.add_message(request, messages.INFO, message)
            return HttpResponseRedirect(reverse('project:issue_detail',
                                                args=[current_project.id,current_issue.id, ]))

        return HttpResponseRedirect(reverse('project:issue_detail',
                                            args=[current_project.id, current_issue.id, ]))


