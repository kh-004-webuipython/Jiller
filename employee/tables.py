import django_tables2 as tables
from django_tables2.utils import A
from .models import Employee


class EmployeeTable(tables.Table):
    id = tables.Column()
    name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')})
    role = tables.Column(attrs={'td': {'width': '10%'}})
    loged = tables.BooleanColumn(attrs={'td': {'width': '10%'}})

    class Meta:
        model = Employee
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id')
        fields = ['name', 'role', 'loged']
