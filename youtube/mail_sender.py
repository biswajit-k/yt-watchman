import smtplib
from email.message import EmailMessage
from youtube.env_details import env_details

def send_mail(to, subject, content):

    SENDER_MAIL = env_details['SENDER_EMAIL']
    SENDER_PASS = env_details['SENDER_PASS']
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_MAIL
    msg['To'] = to
    msg.set_content(content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_MAIL, SENDER_PASS)
        smtp.send_message(msg)

    print("mail sent!")