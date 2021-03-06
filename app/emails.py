from flask import render_template
from flask.ext.mail import Message
from app import app, mail
from config import ADMINS
from decorators import async

@async
def send_async_email(msg):
    with app.app_context():
    	print 1111111111111111111
    	mail.send(msg)
    	print 2222222222222222222

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender = sender, recipients = recipients)
    msg.body = text_body
    msg.html = html_body
    send_async_email(msg)



def follower_notification(followed, follower):
    send_email("[petsreviews] %s is now following you!" % follower.username,
        ADMINS[0],
        [followed.email],
        render_template("follower_email.txt", 
            user = followed, follower = follower),
        render_template("follower_email.html", 
            user = followed, follower = follower))
    