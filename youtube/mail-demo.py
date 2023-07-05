import smtplib
from email.message import EmailMessage
from youtube.env_details import env_details

EMAIL_ADDRESS = env_details['SENDER_EMAIL']
EMAIL_PASSWORD = env_details['SENDER_PASS']
RECEIVER_LIST = env_details['RECEIVER_LIST']

contacts = RECEIVER_LIST

msg = EmailMessage()
msg['Subject'] = 'Check out Bronx as a puppy!'
msg['From'] = EMAIL_ADDRESS
msg['To'] = contacts
msg.set_content('This is a plain text email')


with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    smtp.send_message(msg)

print("mail sent!")