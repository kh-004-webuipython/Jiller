import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.shortcuts import reverse


def sender(request, email, username, key):
    confirmation_link = request.build_absolute_uri(
        reverse('general:confirmation', kwargs={'username': username,
                                                'key': key}))
    fromaddr = 'webui.python@gmail.com'
    toaddr = email

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = 'Confirmation email'
    body = 'Click %s to confirm your email' % confirmation_link
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('webui.python@gmail.com', 'Jiller2017')
    email_info = msg.as_string()
    server.sendmail(fromaddr, toaddr, email_info)
    server.quit()
