from django import forms
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _

from employee.models import Employee


class AuthFormMixin(object):
    def __init__(self, *args, **kwargs):
        super(AuthFormMixin, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'date_birth':
                field.widget.attrs.update(
                    {'class': 'form-control date-picker', 'data-date-format': 'yyyy-mm-dd',
                     'placeholder': field.label})
            else:
                field.widget.attrs.update({'class': 'form-control', 'placeholder': field.label})


class LoginForm(AuthFormMixin, forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255, widget=forms.PasswordInput)


class RegistrationForm(AuthFormMixin, forms.ModelForm):
    DEVELOPER = 'developer'
    PRODUCT_OWNER = 'product owner'
    SCRUM_MASTER = 'scrum master'
    EMPLOYEE_ROLES_CHOICES = (
        (DEVELOPER, _('Developer')),
        (PRODUCT_OWNER, _('Product Owner')),
        (SCRUM_MASTER, _('Scrum Master'))
    )
    password_confirmation = forms.CharField(label=_('Confirm Password'),
                                            max_length=255,
                                            widget=PasswordInput)
    role = forms.ChoiceField(label=_('Role'), choices=EMPLOYEE_ROLES_CHOICES)
    date_birth = forms.DateField(label=_('Date birth'), required=False)

    class Meta:
        model = Employee
        fields = ['username', 'password', 'password_confirmation', 'email',
                  'first_name', 'last_name', 'role', 'date_birth', 'photo']
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
                RegistrationForm.SCRUM_MASTER):
            self.add_error('role', _('Wrong user role'))
