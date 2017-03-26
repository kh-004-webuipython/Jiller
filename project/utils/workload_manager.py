from django.db.models import Q
from project.models import Sprint, Issue
from employee.models import Employee
from django.http import HttpResponse
from waffle import flag_is_active


WEEK_DAYS = 7
WORK_DAYS = 5
WORK_HOURS = 8


def put_issue_back_to_pool(request, pk, issue, relate):
    current_sprint = None
    if relate == 'new_sprint':
        current_sprint = Sprint.objects.get(project=pk, status=Sprint.NEW)
    elif relate == 'active_sprint':
        current_sprint = Sprint.objects.get(project=pk, status=Sprint.ACTIVE)
    elif relate == 'backlog':
        if flag_is_active(request, 'return_issue_to_backlog'):
            if not issue.root:
                issue.type = Issue.USER_STORY
        else:
            return HttpResponse('The issue can not be returned back to backlog.',
                                status=403)

    issue.status = Issue.NEW
    issue.sprint = current_sprint
    issue.employee = None


def assign_issue(pk, employee, issue, sprint_status):
    if not issue.estimation:
        return HttpResponse('The issue has to be estimated', status=403)
    employee = Employee.objects.get(pk=employee)
    issue.employee = employee
    if issue.type == Issue.USER_STORY:
        issue.type = Issue.TASK
    if not issue.sprint:
        sprint = Sprint.objects.get(project=pk, status=sprint_status)
        issue.sprint = sprint


def get_pool(pk, sprint_status):
    issues_log = None
    if sprint_status in [Sprint.NEW, Sprint.ACTIVE]:
        issues_log = Issue.objects.filter(project=pk)\
                         .filter(sprint__status=sprint_status) \
                         .filter(employee__isnull=True).order_by("order")[:10]
    if sprint_status == 'backlog':
        issues_log = Issue.objects.filter(project=pk).filter(sprint__isnull=True) \
                         .filter(~Q(status='deleted')).order_by("order")[:10]

    return issues_log


def calc_work_hours(sprint):
    duration = sprint.duration
    change = duration % WEEK_DAYS \
        if duration % WEEK_DAYS < WORK_DAYS + 1 else WORK_DAYS
    sprint_hours = duration / WEEK_DAYS * (WORK_DAYS * WORK_HOURS) + change * WORK_HOURS

    return sprint_hours
