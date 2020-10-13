from flask import current_app, url_for, render_template
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from app import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()


def send_confirmation_email(user_email):
    """ Email confirmation section """

    confirm_serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
 
    confirm_url = url_for(
        'auth.confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
    
    
    html = render_template(
        'email/confirmation.html',
        confirm_url=confirm_url)
 
    send_email('[Number 16] Confirm Your Email Address',
                sender=current_app.config['ADMINS'][0], 
                recipients=[user_email],
                text_body=None,
                html_body=render_template('email/confirmation.html' , confirm_url=confirm_url))


def send_user_email(sender, recipients, subject, body, user):
    """ User to User email section """
    
    send_email('[Number 16]' + subject,
                sender=sender,
                recipients=recipients,
                text_body=None,
                html_body=render_template('email/user_email.html', body=body, user=user)
                )
