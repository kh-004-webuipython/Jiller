from django import forms
from django.core.exceptions import ValidationError
from django.forms import PasswordInput
from django.utils.translation import ugettext_lazy as _

from workflow.models import Employee
from .models import Project
from django.forms import ModelForm


class DateInput(forms.DateInput):
    input_type = 'date'


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255, widget=PasswordInput)


class RegistrationForm(forms.ModelForm):
    password_confirmation = forms.CharField(label='Confirm Password', max_length=255, widget=PasswordInput)
    email_confirmation = forms.CharField(label='Confirm Email', max_length=255, required=False)

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