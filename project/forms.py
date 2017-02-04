import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Project, Sprint, Issue, IssueComment


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
        if start_date > end_date:
            self.add_error('end_date', _('End date cant\'t be earlies than start date'))


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = '__all__'


class CreateIssueForm(IssueForm):
    def clean_title(self):
        cleaned_data = super(IssueForm, self).clean()
        title = cleaned_data.get('title')
        if Issue.objects.filter(title=title):
            raise forms.ValidationError('This title is already use')
        return title


class SprintCreateForm(forms.ModelForm):
    issue = forms.ModelMultipleChoiceField(queryset=Issue.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project', None)
        super(SprintCreateForm, self).__init__(*args, **kwargs)
        if self.project:
            self.fields['issue'].queryset = self.project.issue_set.filter(sprint=None)

    def clean_status(self):
        if self.cleaned_data['status'] == Sprint.ACTIVE and self.project.sprint_set.filter(
                status=Sprint.ACTIVE).exists():
            raise forms.ValidationError(
                "You are already have an active sprint."
            )
        return self.cleaned_data['status']

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and datetime.date.today() > end_date:
            self.add_error('end_date', _('End date cant\'t be earlier than start date'))

    class Meta:
        model = Sprint
        fields = ['title', 'end_date', 'status']
        widgets = {
            'end_date': DateInput(),
        }


class IssueCommentCreateForm(forms.ModelForm):
    class Meta:
        model = IssueComment
        fields = ['text']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'})
        }


# class TeamForm(forms.ModelForm):
#     class Meta:
#         model = ProjectTeam
#         fields = '__all__'


class EditIssueForm(IssueForm):
    pass





