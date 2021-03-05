from os import getenv

from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.models import Invitations, Teacher
from server.tasks.commons import send_mail_with_html

logger = get_task_logger(__name__)


@celery.task(bind=True)
def send_confirmation_instructions(self, teacher_id):
    try:
        teacher = Teacher.query.filter_by(id=teacher_id).first()
        confirmation_link = teacher.generate_confirmation_link()

        message = Message(subject="Confirm your account")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html(message,
                            'account_confirmation.html.j2',
                            confirmation_link=confirmation_link)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(bind=True)
def send_account_recovery_instructions(self, email):
    teacher = Teacher.query.filter_by(email=email).first()

    if teacher is None:
        return ""
    try:
        recovery_link = teacher.get_reset_link()

        message = Message(subject="Recover your account")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html(message,
                            'account_recovery.html.j2',
                            recovery_link=recovery_link)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(bind=True)
def send_user_invite(self, invite_email):
    try:
        invite = Invitations.query.filter_by(email=invite_email, active=True).first()
        teacher = Teacher.query.filter_by(id=invite.invitation_from_id).first()
        message = Message(subject="Your invite is here!")
        message.recipients = ["{}".format(invite.email)]
        signup_url = f"https://{ getenv('CLIENT_URL', 'portal.zenteach.co.uk') }/signup"

        send_mail_with_html(message,
                            'user_invite.html.j2',
                            inviter=str(teacher),
                            client_url=signup_url,
                            invite_token=invite.token)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)
