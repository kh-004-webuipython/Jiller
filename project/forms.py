import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from general.tasks import send_assign_email_task
from employee.models import IssueLog
from general.forms import FormControlMixin
from .models import Project, Sprint, Issue, ProjectTeam, IssueComment


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if end_date and start_date > end_date:
            self.add_error('end_date',
                           _('End date cant\'t be earlies than start date'))


class IssueForm(forms.ModelForm):
    def __init__(self, user, project, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['sprint'].queryset = Sprint.objects.filter(
            project=project.id)
        self.fields['root'].queryset = Issue.objects.filter(
            project=project.id).filter(status=('new' or 'in progress'))
        self.fields['employee'].queryset = ProjectTeam.objects.filter(
            project=project)[0].employees.filter(
            groups__pk__in=[1, 2])
        if user.groups.filter(id=3):
            self.fields['type'].choices = [('User_story', 'User story'), ]
        elif user.groups.filter(id__in=(1, 2, 4)):
            self.fields['type'].choices = [('Task', 'Task'), ('Bug', 'Bug'), ]

    def clean_status(self):
        cleaned_data = super(IssueForm, self).clean()
        status = cleaned_data.get('status')
        sprint = cleaned_data.get('sprint')
        if not sprint and status != Issue.NEW:
            raise forms.ValidationError(
                'The issue unrelated to sprint has to be NEW')
        return status

    def clean_estimation(self):
        cleaned_data = super(IssueForm, self).clean()
        estimation = cleaned_data.get('estimation')
        sprint = cleaned_data.get('sprint')
        if sprint and not estimation:
            raise forms.ValidationError(
                'The issue related to sprint has to be estimated')
        return estimation

    def send_email(self, user_id, issue_id):
        employee = self.cleaned_data['employee']
        if employee and employee.email:
            email = employee.email
            send_assign_email_task.delay(email, user_id, issue_id)

    class Meta:
        model = Issue
        fields = ['root', 'type', 'sprint', 'employee', 'title', 'description',
                  'status', 'estimation', 'order']


class IssueFormForEditing(IssueForm):
    def __init__(self, *args, **kwargs):
        super(IssueFormForEditing, self).__init__(*args, **kwargs)
        self.fields.pop('order')


class CreateIssueForm(IssueForm):
    def clean_title(self):
        cleaned_data = super(IssueForm, self).clean()
        title = cleaned_data.get('title')
        if Issue.objects.filter(title=title):
            raise forms.ValidationError('This title is already use')
        return title


class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = ProjectTeam
        fields = ['title']

    def clean_title(self):
        cleaned_data = super(CreateTeamForm, self).clean()
        title = cleaned_data.get('title')
        if ProjectTeam.objects.filter(title=title):
            raise forms.ValidationError('This title is already use')
        return title


class IssueCommentCreateForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'})
        }


class IssueLogForm(FormControlMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.issue = kwargs.pop('issue', None)
        super(IssueLogForm, self).__init__(*args, **kwargs)

    def clean_cost(self):
        cost = self.cleaned_data['cost']
        if cost < 0:
            raise forms.ValidationError(_('Issue log can not be less than 0'))
        if cost + self.issue.get_logs_sum() > self.issue.estimation:
            raise forms.ValidationError(
                _('Your log is greater than issue estimation'))
        return cost

    class Meta:
        model = IssueLog
        fields = ['cost', 'note']


class SprintFinishForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['feedback_text', 'relies_link']
        widgets = {
            'feedback_text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': '10',
                       'style': 'resize: vertical;'}),
            'relies_link': forms.URLInput(attrs={'class': 'form-control'})
        }


class SprintCreateForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['title', 'duration']
