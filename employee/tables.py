import django_tables2 as tables
from django_tables2.utils import A
from django.utils.html import format_html
from .models import Employee
from django.utils.safestring import mark_safe
from project.models import ProjectTeam


class EmployeeTable(tables.Table):
    id = tables.Column()
    name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')}, order_by=('last_name'))
    username = tables.Column()
    email = tables.Column()
    date_joined = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    is_active = tables.BooleanColumn(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Employee
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id')
        fields = ['name', 'username', 'email', 'date_joined', 'is_active']


class ProjectTeamTable(tables.Table):
    id = tables.Column()
    project = tables.Column()
    title = tables.Column()
    members = tables.Column()

    # name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')})
    # role = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
    # move = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = ProjectTeam
        attrs = {"class": "table table-bordered table-striped table-hover table-cur"}
        exclude = ('id')
        fields = ['title', 'project', 'members']


# class ProjectTeamTable(tables.Table):
#     id = tables.Column()
#     team = tables.Column(accessor='ProjectTeam.id')
#     name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')})
#     role = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#     move = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#
#     class Meta:
#         model = Employee
#         attrs = {"class": "table table-bordered table-striped table-hover table-cur"}
#         exclude = ('id')
#         fields = ['team', 'name', 'role', 'move']


# class ProjectTeamEmployeeTable(tables.Table):
#     id = tables.Column()
#     name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')})
#     role = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#     remove = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#
#     class Meta:
#         model = Employee
#         attrs = {"class": "table table-bordered table-striped table-hover table-cur"}
#         exclude = ('id')
#         fields = ['name', 'role', 'remove']
#
#
# class ProjectTeamEmployeeAddTable(tables.Table):
#     id = tables.Column()
#     name = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('id')})
#     role = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#     add = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})
#
#     class Meta:
#         model = Employee
#         attrs = {"class": "table table-bordered table-striped table-hover table-add"}
#         exclude = ('id')
#         fields = ['name', 'role', 'add']