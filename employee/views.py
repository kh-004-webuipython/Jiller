from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from project.models import Issue
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

    return render(request, 'employee/detail.html', generate_tables(employee))


def generate_tables(user):
    data = {}
    online_status = user.online_status()
    data.update({'employee': user, 'online_status': online_status})
    logs = user.issuelog_set.all()
    if logs:
        table_logs = LogsTable(logs)
        data.update({'table_logs': table_logs})

    issues = Issue.objects.filter(employee=user)
    if issues:
        table_issues = IssuesInProfileTable(issues)
        data.update({'table_issues': table_issues})

    projects = user.get_all_projects()
    if projects:
        table_projects = ProjectTable(projects)
        data.update({'table_projects': table_projects})

    comments = user.issuecomment_set.all()
    if comments:
        table_comments = CommentsTable(comments)
        data.update({'table_comments': table_comments})

    return data
