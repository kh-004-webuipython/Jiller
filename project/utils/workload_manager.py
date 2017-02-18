from django.db.models import Q
from project.models import Sprint, Issue
from employee.models import Employee


WEEK_DAYS = 7
WORK_DAYS = 5
WORK_HOURS = 8


def put_issue_back_to_pool(pk, issue, relate):
    current_sprint = None
    if relate == 'new_sprint':
        current_sprint = Sprint.objects.get(project=pk, status=Sprint.NEW)
    issue.sprint = current_sprint
    issue.employee = None


def assign_issue(pk, employee, issue, sprint_status):
    employee = Employee.objects.get(pk=employee)
    issue.employee = employee
    if not issue.sprint:
        sprint = Sprint.objects.get(project=pk, status=sprint_status)
        issue.sprint = sprint


def get_pool(pk, sprint_status):
    if sprint_status == Sprint.NEW:
        issues_log = Issue.objects.filter(project=pk)\
                         .filter(sprint__status=Sprint.NEW) \
                         .filter(employee__isnull=True).order_by("order")[:10]
    else:
        issues_log = Issue.objects.filter(project=pk).filter(sprint__isnull=True) \
                         .filter(~Q(status='deleted')).order_by("order")[:10]

    return issues_log


def calc_work_hours(sprint):
    duration = sprint.duration
    change = duration % WEEK_DAYS \
        if duration % WEEK_DAYS < WORK_DAYS + 1 else WORK_DAYS
    sprint_hours = duration / WEEK_DAYS * (WORK_DAYS * WORK_HOURS) + change * WORK_HOURS

    return sprint_hours
