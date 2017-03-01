from django.http.response import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from employee.filters import EmployeeFilter
from project.models import Issue
from .models import Employee
from .tables import EmployeeTable
from django_tables2 import RequestConfig
from django.conf import settings


def employee_index_view(request):
    queryset = Employee.objects.all()
    employee_filter = EmployeeFilter(request.GET, queryset=queryset)
    table = EmployeeTable(employee_filter.qs)
    RequestConfig(request,
                  paginate={
                      'per_page': settings.PAGINATION_PER_PAGE}).configure(
        table)
    return render(request, 'employee/list.html',
                  {'table': table, 'filter': employee_filter})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    online_status = employee.online_status()
    return render(request, 'employee/detail.html', {'employee': employee,
                                                    'online_status': online_status})
