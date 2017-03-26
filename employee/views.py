from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from project.models import Issue, Project, IssueComment
from .models import Employee, IssueLog
from .tables import EmployeeTable, LogsTable
from project.tables import IssuesInProfileTable, ProjectTable, CommentsTable
from django_tables2 import RequestConfig
from django.conf import settings


def employee_index_view(request):
    table = EmployeeTable(Employee.objects.all())
    RequestConfig(request, paginate={'per_page':
                                settings.PAGINATION_PER_PAGE}).configure(table)
    return render(request, 'employee/list.html', {'table': table})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)

    return render(request, 'employee/detail.html', generate_tables(employee,
                                                                   request.user))


def security_note_list(data, user):
    if data:
        if data.model == Issue:
            return data.filter(project__in=user.get_all_projects()).order_by('-order')
        if data.model == Project:
            return data.filter(id__in=user.get_all_projects())
        if data.model == IssueLog or data.model == IssueComment:
            return data.filter(issue__project__in=user.get_all_projects())
    return []


def generate_tables(user, req_user):
    data = {}
    online_status = user.online_status()
    data.update({'employee': user, 'online_status': online_status})

    logs = security_note_list(user.issuelog_set.all(), req_user)
    if logs:
        table_logs = LogsTable(logs)
        data.update({'table_logs': table_logs})

    issues = security_note_list(Issue.objects.filter(employee=user), req_user)
    if issues:
        table_issues = IssuesInProfileTable(issues)
        data.update({'table_issues': table_issues})

    projects = security_note_list(user.get_all_projects(), req_user)
    if projects:
        table_projects = ProjectTable(projects)
        data.update({'table_projects': table_projects})

    comments = security_note_list(user.issuecomment_set.all(), req_user)
    if comments:
        table_comments = CommentsTable(comments)
        data.update({'table_comments': table_comments})

    return data
