from celery.task import task

from general.emails import send_assign_email


@task(name="send_assign_email_task")
def send_assign_email_task(email, user_id, issue_id):
    """sends an email when feedback form is filled successfully"""
    return send_assign_email(email, user_id, issue_id)
