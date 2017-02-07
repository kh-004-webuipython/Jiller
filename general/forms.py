from django import forms
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _

from employee.models import Employee


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255,
                               widget=PasswordInput)


class RegistrationForm(forms.ModelForm):
    DEVELOPER = 'developer'
    PRODUCT_OWNER = 'product owner'
    SCRUM_MASTER = 'scrum master'
    PROJECT_MANAGER = 'project manager'
    EMPLOYEE_ROLES_CHOICES = (
        (DEVELOPER, _('Developer')),
        (PRODUCT_OWNER, _('Product Owner')),
        (SCRUM_MASTER, _('Scrum Master')),
        (PROJECT_MANAGER, _('Project Manager'))
    )
    password_confirmation = forms.CharField(label=_('Confirm Password'),
                                            max_length=255,
                                            widget=PasswordInput)
    role = forms.ChoiceField(label=_('Role'), choices=EMPLOYEE_ROLES_CHOICES)

    class Meta:
        model = Employee
        fields = ['username', 'password', 'password_confirmation', 'email',
                  'first_name', 'last_name', 'role']
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('password_confirmation')
        email = cleaned_data.get('email')
        if password != confirm_password:
            self.add_error('password',
                           _('Password do not equal confirm password'))
        user = Employee.objects.filter(
            username=cleaned_data['username']).first()
        if user is not None:
            self.add_error('username',
                           _('User with this username already exists'))
        user = Employee.objects.filter(email=email).first()
        if user is not None:
            self.add_error('email', _('User with this email already exists'))
        role = cleaned_data.get('role')
        if role not in (
        RegistrationForm.DEVELOPER, RegistrationForm.PRODUCT_OWNER,
        RegistrationForm.SCRUM_MASTER, RegistrationForm.PROJECT_MASTER):
            self.add_error('role', _('Wrong user role'))
