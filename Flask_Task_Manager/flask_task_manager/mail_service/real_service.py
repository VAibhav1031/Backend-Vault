from . import MailService
from flask_mail import Message
from flask_task_manager import mail
from flask import render_template


class RealMailService(MailService):
    def __init__(self, app):
        self.sender = app.config.get("MAIL_USERNAME", "noreply@demo.com")
        self.app = app

    def send_mail(self, user, otp):
        msg = Message(
            "Password reset Request", sender=self.sender, recipients=[user.email]
        )
        msg.body = render_template(
            "reset_password.txt", username=user.username, OTP=otp
        )
        msg.html = render_template(
            "reset_password.html", username=user.username, OTP=otp
        )
        mail.send(msg)
