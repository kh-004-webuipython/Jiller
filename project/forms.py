from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Project, Sprint, Issue


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'start_date','end_date']
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


# class TeamForm(forms.ModelForm):
#     class Meta:
#         model = ProjectTeam
#         fields = '__all__'


class SprintCreateForm(forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['title', 'project', 'team', 'start_date', 'end_date',
                  'order', 'status']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }
