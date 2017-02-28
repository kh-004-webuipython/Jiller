def user_variator(self, user, project):
    if user.groups.all():
        if user.groups.filter(id=2):
            del self.fields['type']

        if user.groups.filter(id=3):
            del self.fields['type']
            del self.fields['root']
            del self.fields['estimation']


def check_if_issue_assigned(form):
    return 'self_assign' in form.cleaned_data and form.cleaned_data['self_assign']

def check_issue_add_to_sprint(form):
    return 'add_sprint' in form.cleaned_data and form.cleaned_data['add_sprint']
