import django_tables2 as tables
from django_tables2.utils import A
from .models import Employee


class EmployeeTable(tables.Table):
    details = tables.Column()
    name = tables.Column()
    role = tables.Column()
    loged = tables.BooleanColumn()

    class Meta:
        model = Employee
        attrs = {"class": "table table-bordered table-striped table-hover"}
        fields = ['details', 'name', 'role', 'loged']
