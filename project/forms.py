import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

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
    def __init__(self, project, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['sprint'].queryset = Sprint.objects.filter(
            project=project.id)
        self.fields['root'].queryset = Issue.objects.filter(
            project=project.id).filter(status=('new' or 'in progress'))

    class Meta:
        model = Issue
        fields = ['root', 'sprint', 'employee', 'title', 'description',
                  'status', 'estimation', 'order']


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


class SprintCreateForm(forms.ModelForm):
    issue = forms.ModelMultipleChoiceField(queryset=Issue.objects.all(),
                                           required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(SprintCreateForm, self).__init__(*args, **kwargs)
        if self.project:
            self.fields['issue'].queryset = self.project.issue_set.filter(
                sprint=None)

    def clean_status(self):
        if self.cleaned_data['status'] == Sprint.ACTIVE and self.project.sprint_set.filter(
                status=Sprint.ACTIVE).exists():
            raise forms.ValidationError(
                "You are already have an active sprint."
            )
        return self.cleaned_data['status']

    class Meta:
        model = Sprint
        fields = ['title', 'duration', 'status', 'issue']


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
            raise forms.ValidationError(_('Your log is greater than issue estimation'))
        return cost

    class Meta:
        model = IssueLog
        fields = ['cost', 'note']
