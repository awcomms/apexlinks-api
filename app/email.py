from flask import render_template
from flask_mail import Message
from app import mail
from flask import current_app
from threading import Thread

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()

def send_reset_password(user):
    token = user.set_reset_password_token()
    send_email(
        'Reset password',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/reset_password/txt.txt', user=user, token=token),
        html_body=render_template('email/reset_password/htm.htm', user=user, token=token))

def send_renewal_failure(user):
    send_email(
        'Automatic subscription renewal failure',
        sender=current_app.config['ADMINS'][0],
        recipients=[user.email],
        text_body=render_template('email/renewal_failure/txt.txt', user=user),
        html_body=render_template('email/renewal_failure/htm.htm', user=user))

