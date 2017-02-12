import django_tables2 as tables
from django_tables2.utils import A
from .models import ProjectTeam, Project, Sprint, Issue


class ProjectTable(tables.Table):
    id = tables.Column()
    title = tables.LinkColumn('project:detail', kwargs={"project_id": A('id')},
                              attrs={'td': {'width': '30%'}})
    start_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '2%'}})
    end_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '2%'}})
    is_active = tables.BooleanColumn(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Project
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        exclude = ('id', 'is_active', 'description')


class SprintsListTable(tables.Table):
    id = tables.Column()
    project = tables.Column()
    title = tables.LinkColumn('project:sprint_detail', kwargs={"project_id": A('project.id'),
                              "sprint_id": A('id')}, attrs={'td': {'width': '30%'}})
    team = tables.LinkColumn('project:team', kwargs={"project_id": A('project.id')},
                             attrs={'td': {'width': '30%'}})
    start_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    end_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    status = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Sprint
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id', 'project', 'order')
        fields = ['title', 'team', 'start_date', 'end_date', 'status']


class IssuesTable(tables.Table):
    id = tables.Column()
    root = tables.Column(attrs={'td': {'width': '10%'}})
    project = tables.Column()
    author = tables.LinkColumn('employee:detail', kwargs={"employee_id": A('author.id')},
                             attrs={'td': {'width': '20%'}})
    title = tables.LinkColumn('project:issue_detail', kwargs={"project_id": A('project.id'),
                              "issue_id": A('id')}, attrs={'td': {'width': '20%'}})
    description = tables.Column(attrs={'td': {'width': '30%'}})
    status = tables.Column(attrs={'td': {'width': '10%'}})
    order = tables.Column(attrs={'td': {'width': '10%'}})

    class Meta:
        model = Issue
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id', 'project', 'sprint', 'employee', 'estimation')
        fields = ['title', 'description', 'root', 'author', 'status', 'order']




