from django.shortcuts import render, get_object_or_404
from .models import Employee
from .tables import EmployeeTable
from django_tables2 import SingleTableView, RequestConfig


# def employee_index_view(request):
#     employee_list = Employee.objects.all()
#     return render(request, 'employee/list.html', {'employee_list': employee_list})


def employee_index_view(request):
    table = EmployeeTable(Employee.objects.all())
    RequestConfig(request).configure(table)
    return render(request, 'employee/list.html', {'table': table})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    return render(request, 'employee/detail.html', {'employee': employee})

