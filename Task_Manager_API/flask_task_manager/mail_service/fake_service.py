from . import MailService


class FakeMailService(MailService):
    def __init__(self, app):
        self.app = app
        self.sent_mails = []

    def send_mail(self, user, otp):
        fake_msg = {
            "to": user.email,
            "subject": "Password reset Request [Fake] ",
            "body": f"OTP : {otp}   for user {user.username}",
        }
        self.sent_mails.append(fake_msg)
        self.app.logger.info(f"[Fake Mail] {fake_msg}")
