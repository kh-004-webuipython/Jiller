from django import forms
from project.models import Sprint


def user_variator(self, user, project):
    if user.groups.all():
        if Sprint.objects.filter(project=project.pk, status=Sprint.NEW):
            self.fields['add_sprint'] = forms.BooleanField(label='Add to new sprint', required=False)

        if user.groups.filter(id=1):
            self.fields['self_assign'] = forms.BooleanField(label='Assign yourself',
                                                            required=False)

        if user.groups.filter(id=3):
            del self.fields['type']
            del self.fields['root']
            del self.fields['estimation']


def check_if_issue_assigned(form):
    return 'self_assign' in form.cleaned_data and form.cleaned_data['self_assign']

def check_issue_add_to_sprint(form):
    return 'add_sprint' in form.cleaned_data and form.cleaned_data['add_sprint']
