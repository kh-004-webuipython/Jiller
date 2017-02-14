from django.conf import settings
from django.core.mail import EmailMessage
from django.template import Context
from django.template.loader import render_to_string, get_template

from employee.models import Employee
from project.models import Issue


def send_assign_email(email, user_id, issue_id):
    user = Employee.objects.get(pk=user_id)
    issue = Issue.objects.get(pk=issue_id)

    # message = str(user.first_name) + ' ' + str(
    #     user.last_name) + ' assigned you to issue : ' + issue.title
    user_name = str(user.first_name) + ' ' + str(user.last_name)
    c = Context({'email': email, 'user': user_name, 'issue': issue})

    email_subject = render_to_string(
        'email/feedback_email_subject.txt', c).replace('\n', '')
    email_body = get_template('email/assign_email_template.html').render(Context(c))

    email = EmailMessage(
        email_subject, email_body, settings.DEFAULT_FROM_EMAIL,
        [email], [],
        headers={'Reply-To': email}
    )
    email.content_subtype = 'html'

    return email.send(fail_silently=False)
