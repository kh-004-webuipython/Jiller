from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string, get_template
from django.urls import reverse
from employee.models import Employee
from project.models import Issue, Sprint


def send_assign_email(email, user_id, issue_id):
    user = Employee.objects.get(pk=user_id)
    issue = Issue.objects.get(pk=issue_id)
    issue_url = settings.JILLER_HOST + reverse('project:issue_detail', kwargs={'project_id':issue.project_id, 'issue_id':issue.id})
    user_name = str(user.first_name) + ' ' + str(user.last_name)
    c = Context({'email': email, 'user': user_name, 'issue': issue, 'issue_url':issue_url})

    email_subject = render_to_string(
        'email/email_subject.txt', c).replace('\n', '')
    email_body = get_template('email/assign_email_template.html').render(Context(c))

    email = EmailMessage(
        email_subject, email_body, settings.DEFAULT_FROM_EMAIL,
        [email], [],
        headers={'Reply-To': email}
    )
    email.content_subtype = 'html'

    return email.send(fail_silently=False)


def send_email_after_sprint_start(email, user_id, sprint_id):
    user = Employee.objects.get(pk=user_id)
    sprint = Sprint.objects.get(pk=sprint_id)
    sprint_url = settings.JILLER_HOST + reverse('project:sprint_active', kwargs={
        'project_id': sprint.project_id})
    user_name = str(user.first_name) + ' ' + str(user.last_name)
    c = Context({'email': email, 'user': user_name, 'sprint': sprint, 'sprint_url': sprint_url})

    email_subject = render_to_string(
        'email/email_subject.txt', c).replace('\n', '')
    email_body = get_template('email/after_sprint_start_email_template.html').render(Context(c))

    email = EmailMessage(
        email_subject, email_body, settings.DEFAULT_FROM_EMAIL,
        [email], [],
        headers={'Reply-To': email}
    )
    email.content_subtype = 'html'

    return email.send(fail_silently=False)
