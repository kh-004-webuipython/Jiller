import django_tables2 as tables
from django_tables2.utils import A
from .models import ProjectTeam, Project, Sprint


class ProjectTable(tables.Table):
    id = tables.Column()
    title = tables.LinkColumn('project:detail', kwargs={"project_id": A('id')},
                              attrs={'td': {'width': '30%'}})
    description = tables.Column()
    start_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    end_date = tables.DateColumn(attrs={'td': {'align': 'center', 'width': '10%'}})
    is_active = tables.BooleanColumn(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Project
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        exclude = ('id', 'is_active')


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