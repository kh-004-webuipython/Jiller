from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255)


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=255)
    password = forms.CharField(label='Password', max_length=255)
    email = forms.CharField(label='Email', max_length=255)
    last_name = forms.CharField(label='Last name', max_length=255)
    first_name = forms.CharField(label='First name', max_length=255)


class EditIssueForm(forms.Form):
    title = forms.CharField(label='Sprint', max_length=255)
    author = forms.CharField(label='Author', max_length=255)
    employee = forms.CharField(label='Employee', max_length=255)
    title = forms.CharField(label='Title', max_length=255)
    description = forms.CharField(label='Description', widget=forms.Textarea)
    status = forms.CharField(label='Status', max_length=255)


