import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from PIL import Image

from general.tasks import send_assign_email_task
from employee.models import IssueLog
from general.forms import FormControlMixin
from .models import Project, Sprint, Issue, ProjectTeam, IssueComment, \
    ProjectNote

from .utils.user_variator import user_variator


class DateInput(forms.DateInput):
    input_type = 'date'


class ProjectForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'start_date', 'description', 'end_date']
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


class IssueForm(FormControlMixin, forms.ModelForm):
    def __init__(self, user, project, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        self.fields['root'].queryset = Issue.objects.filter(
            project=project.id).filter(status=('new' or 'in progress'))
        self.fields['type'].choices = [('Task', 'Task'), ('Bug', 'Bug'), ]
        user_variator(self, user, project)

    def clean_status(self):
        cleaned_data = super(IssueForm, self).clean()
        status = cleaned_data.get('status')
        sprint = cleaned_data.get('sprint')
        if not sprint and status == (Issue.IN_PROGRESS or Issue.RESOLVED):
            raise forms.ValidationError(
                'The issue unrelated to sprint can\'t be in progress or resolved.')
        return status

    def clean_estimation(self):
        cleaned_data = super(IssueForm, self).clean()
        estimation = cleaned_data.get('estimation')
        add_sprint = cleaned_data.get('add_sprint')
        if add_sprint and not estimation:
            raise forms.ValidationError(
                'The issue related to sprint has to be estimated')
        return estimation

    def send_email(self, base_url, user_id, issue_id):
        employee = Issue.objects.get(pk=issue_id).employee
        if employee and employee.email:
            email = employee.email
            send_assign_email_task.delay(base_url, email, user_id, issue_id)

    class Meta:
        model = Issue

        fields = ['title', 'estimation', 'type', 'root', 'description',
                  'status', 'order']
        labels = {
            'root': _('Parent issue'),
        }

class IssueFormForEditing(IssueForm):
    def __init__(self, *args, **kwargs):
        super(IssueFormForEditing, self).__init__(*args, **kwargs)
        self.fields.pop('order')
        if 'add_sprint' in self.fields:
            self.fields.pop('add_sprint')
        if 'self_assign' in self.fields:
            self.fields.pop('self_assign')


class CreateIssueForm(IssueForm):
    def __init__(self, *args, **kwargs):
        super(CreateIssueForm, self).__init__(*args, **kwargs)
        self.fields.pop('status')


    def clean_title(self):
        cleaned_data = super(CreateIssueForm, self).clean()
        title = cleaned_data.get('title')
        if Issue.objects.filter(title=title):
            raise forms.ValidationError('This title is already use')
        return title


class IssueFormForSprint(CreateIssueForm):
    def __init__(self, *args, **kwargs):
        super(IssueFormForSprint, self).__init__(*args, **kwargs)
        if 'add_sprint' in self.fields:
            self.fields.pop('add_sprint')


class CreateTeamForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = ProjectTeam
        fields = ['title']

    def clean_title(self):
        cleaned_data = super(CreateTeamForm, self).clean()
        title = cleaned_data.get('title')
        if ProjectTeam.objects.filter(title=title):
            raise forms.ValidationError('This title is already use')
        return title


class IssueCommentCreateForm(FormControlMixin, forms.ModelForm):
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
            raise forms.ValidationError(
                _('Your log is greater than issue estimation'))
        return cost

    class Meta:
        model = IssueLog
        fields = ['cost', 'note']


class SprintFinishForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['feedback_text', 'release_link']
        widgets = {
            'feedback_text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': '10',
                       'style': 'resize: vertical;'}),
            'release_link': forms.URLInput(attrs={'class': 'form-control'})
        }


class SprintCreateForm(FormControlMixin, forms.ModelForm):
    class Meta:
        model = Sprint
        fields = ['title', 'duration']


class NoteForm(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['title', 'content']


class NoteFormWithImage(forms.ModelForm):
    class Meta:
        model = ProjectNote
        fields = ['title', 'content', 'picture']

    def clean_picture(self):
        MAX_PIXEL_SIZE = 5000
        MAX_FILE_SIZE = 10 # MB
        IMG_EXTENSION = ['jpeg', 'pjpeg', 'jpg', 'png', 'gif']
        image = self.cleaned_data['picture']
        if image:
            img = Image.open(image)
            w, h = img.size

            # validate dimensions
            max_width = max_height = MAX_PIXEL_SIZE
            if w > max_width or h > max_height:
                raise forms.ValidationError(
                    _('Please use an image that is smaller or equal to '
                      '%s x %s pixels.' % (max_width, max_height)))

            # validate content type
            main, sub = image.content_type.split('/')
            if not (main == 'image' and sub.lower() in IMG_EXTENSION):
                raise forms.ValidationError(
                    _('Please use a JPEG or PNG image.'))

            # validate file size
            if len(image) > (MAX_FILE_SIZE * 1024 * 1024):
                raise forms.ValidationError(
                    _('Image file too large ( maximum 10mb )'))
        else:
            raise forms.ValidationError(_("Couldn't read uploaded image"))
        return image
