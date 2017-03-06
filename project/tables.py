import django_tables2 as tables
from django_tables2.utils import A
from .models import ProjectTeam, Project, Sprint, Issue, IssueComment
from employee.tables import EmployeeTable


class ProjectTable(tables.Table):
    id = tables.Column()
    title = tables.LinkColumn('project:detail', kwargs={"project_id": A('id')},
                              attrs={'td': {'width': '30%'}})
    start_date = tables.DateColumn(attrs={'td': {'align': 'center',
                                                 'width': '2%'}})
    end_date = tables.DateColumn(attrs={'td': {'align': 'center',
                                               'width': '2%'}})
    is_active = tables.BooleanColumn(attrs={'td': {'align': 'center',
                                                   'width': '10%'}})

    class Meta:
        model = Project
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        exclude = ('id', 'is_active', 'description')


class SprintsListTable(tables.Table):
    id = tables.Column()
    project = tables.Column()
    title = tables.LinkColumn('project:sprint_detail',
                              kwargs={"project_id": A('project.id'),
                              "sprint_id": A('id')},
                              attrs={'td': {'width': '30%'}})
    start_date = tables.DateColumn(attrs={'td': {'align': 'center',
                                                 'width': '10%'}})
    end_date = tables.DateColumn(attrs={'td': {'align': 'center',
                                               'width': '10%'}})
    status = tables.Column(attrs={'td': {'align': 'center', 'width': '10%'}})

    class Meta:
        model = Sprint
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id', 'project', 'order')
        fields = ['title', 'start_date', 'end_date', 'status']


class IssuesTable(tables.Table):
    id = tables.Column()
    root = tables.Column(attrs={'td': {'width': '10%'}})

    author = tables.LinkColumn('employee:detail',
                               kwargs={"employee_id": A('author.id')},
                               attrs={'td': {'width': '20%'}})
    title = tables.LinkColumn('project:issue_detail',
                              kwargs={"project_id": A('project.id'),
                              "issue_id": A('id')},
                              attrs={'td': {'width': '20%'}})
    description = tables.Column(attrs={'td': {'width': '30%'}})
    status = tables.Column(attrs={'td': {'width': '10%'}})
    order = tables.Column(attrs={'td': {'width': '10%'}})

    class Meta:
        model = Issue
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id', 'project', 'sprint', 'employee', 'estimation')
        fields = ['title', 'description', 'root', 'author', 'status', 'order']


class IssuesInProfileTable(IssuesTable):
    estimation = tables.Column(attrs={'td': {'width': '5%'}})
    author = tables.LinkColumn('employee:detail',
                               kwargs={"employee_id": A('author.id')},
                               attrs={'td': {'width': '10%'}})
    project = tables.LinkColumn('project:detail',
                                kwargs={"project_id": A('project.id')},
                                attrs={'td': {'width': '12%'}})
    status = tables.Column(attrs={'td': {'width': '5%'}})
    sprint = tables.LinkColumn('project:sprint_detail',
                              kwargs={"project_id": A('project.id'),
                              "sprint_id": A('sprint.id')},
                               attrs={'td': {'width': '10%'}})

    class Meta:
        model = Issue
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('root', 'description', 'order')
        fields = ['author', 'title', 'status', 'estimation',
                  'project', 'sprint']
        order_by = 'sprint'


class ProjectTeamTable(EmployeeTable):
    get_role = tables.Column(attrs={'td': {'width': '30%'}},
                             verbose_name='Role',
                             order_by=('groups',))

    class Meta:
        exclude = ('id', 'email', 'date_joined')
        fields = ['get_full_name', 'get_role']
        order_by = ('get_role',)


class CommentsTable(tables.Table):
    issue = tables.LinkColumn('project:issue_detail',
                              kwargs={"project_id": A('issue.project.id'),
                                      'issue_id': A('issue.id')},
                              order_by=('issue'), verbose_name='Issue')
    text = tables.Column()
    date_created = tables.Column()

    class Meta:
        model = IssueComment
        attrs = {"class": "table table-bordered table-striped table-hover"}
        fields = ['issue', 'text', 'date_created', ]
        order_by = ('date_created', )