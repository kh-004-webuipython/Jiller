import django_tables2 as tables
from django_tables2.utils import A
from .models import Employee, IssueLog


class EmployeeTable(tables.Table):
    id = tables.Column()
    get_full_name = tables.LinkColumn('employee:detail',
                                      kwargs={"employee_id": A('id')},\
                                      order_by=('last_name'),
                                      verbose_name='Name')
    email = tables.Column()
    get_role = tables.Column(verbose_name='Role')
    date_joined = tables.DateColumn(attrs={'td': {'align': 'center',
                                                  'width': '10%'}})
    is_active = tables.BooleanColumn(attrs={'th': {'style':
                                                       'text-align: center'},
                                            'td': {'align': 'center',
                                                   'width': '10%'}},
                                     verbose_name='In action')
    online_status = tables.Column(verbose_name='Activity',
                                     order_by='last_activity')

    class Meta:
        model = Employee
        attrs = {"class": "table table-bordered table-striped table-hover"}
        exclude = ('id', 'is_active')
        fields = ['get_full_name', 'email', 'get_role',
                  'online_status', 'date_joined']


class LogsTable(tables.Table):
    issue = tables.LinkColumn('project:issue_detail',
                              kwargs={"project_id": A('issue.project.id'),
                                      'issue_id': A('issue.id')},
                              order_by=('issue'), verbose_name='Issue')
    cost = tables.Column(verbose_name='Costs')
    note = tables.Column(verbose_name=('Note'))

    class Meta:
        model = IssueLog
        attrs = {"class": "table table-bordered table-striped table-hover"}
        fields = ['issue', 'cost', 'note', ]
