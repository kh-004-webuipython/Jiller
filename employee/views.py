from django.shortcuts import render, get_object_or_404

from workflow.models import Employee


def employee_index_view(request):
    employee_list = Employee.objects.all()
    return render(request, 'employee/index.html', {'employee_list': employee_list})


def employee_detail_view(request, employee_id):
    employee = get_object_or_404(Employee, pk=employee_id)
    return render(request, 'employee/detail.html', {'employee': employee})
