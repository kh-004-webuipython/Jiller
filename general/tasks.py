from celery.task import task

from general.emails import send_assign_email, send_email_after_sprint_start, send_email_after_sprint_finish


@task(name="send_assign_email_task")
def send_assign_email_task(base_url,email, user_id, issue_id):
    return send_assign_email(base_url,email, user_id, issue_id)


@task(name="send_email_after_sprint_start_task")
def send_email_after_sprint_start_task(base_url,email, user_id, sprint_id):
    return send_email_after_sprint_start(base_url,email, user_id, sprint_id)


@task(name="send_email_after_sprint_finish_task")
def send_email_after_sprint_finish_task(base_url,email, user_id, sprint_id, release_link, feedback_text):
    return send_email_after_sprint_finish(base_url,email, user_id, sprint_id, release_link, feedback_text)
