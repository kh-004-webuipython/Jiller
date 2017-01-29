from django import forms
from django.core.exceptions import ValidationError
from django.forms import PasswordInput, ModelForm
from django.utils.translation import ugettext_lazy as _

from .models import Project, Sprint, Employee, Issue


class DateInput(forms.DateInput):
    input_type = 'date'


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255, widget=PasswordInput)


class RegistrationForm(forms.ModelForm):
    password_confirmation = forms.CharField(label='Confirm Password', max_length=255, widget=PasswordInput)
    email_confirmation = forms.EmailField(label='Confirm Email', max_length=255, required=False)

    class Meta:
        model = Employee
        fields = ['username', 'password', 'password_confirmation', 'email', 'email_confirmation', 'last_name',
                  'first_name', 'role']
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('password_confirmation')
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('email_confirmation')
        if password != confirm_password:
            self.add_error('password', _('Password do not equal confirm password'))
        if email != confirm_email:
            self.add_error('email', _('Email does not equal confirm email'))


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'end_date']
        widgets = {
            'end_date': DateInput(),
        }


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = '__all__'


# class TeamForm(forms.ModelForm):
#     class Meta:
#         model = ProjectTeam
#         fields = '__all__'



class SprintCreateForm(ModelForm):
    class Meta:
        model = Sprint
        fields = ['title', 'project', 'team', 'start_date', 'end_date',
                  'order', 'status']
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput(),
        }
