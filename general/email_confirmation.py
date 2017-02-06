import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def sender(email, username, key):
    li = ['http://127.0.0.1:8000/confirmation', username, key]
    confirmation_link = "/".join(li)
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
