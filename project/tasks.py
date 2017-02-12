from celery.task import task

from project.emails import send_assign_email


@task(name="send_assign_email_task")
def send_assign_email_task(email, user_id, issue_id):
    """sends an email when feedback form is filled successfully"""
    print "Sent feedback email"
    return send_assign_email(email, user_id, issue_id)


# @task(name="project.tasks.add")
# def add(x, y):
#     return x + y