import smtplib
from email.message import EmailMessage

def send_mail(from_id, from_pass, to_id_list, subject, content):

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_id
    msg['To'] = to_id_list
    msg.set_content(content)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_id, from_pass)
        smtp.send_message(msg)

    print("mail sent!")