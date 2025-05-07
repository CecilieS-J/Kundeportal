# webapp/mail.py
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_alert(subject, recipients, body):
    msg = Message(subject, recipients=recipients)
    msg.body = body
    mail.send(msg)
