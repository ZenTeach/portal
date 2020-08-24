from flask_mail import Message
from server import celery
from server.models import Teacher
from server.tasks.commons import send_mail_with_html


@celery.task
def send_confirmation_instructions(teacher_id):
    teacher = Teacher.query.find(teacher_id)
    confirmation_link = teacher.generate_confirmation_link()

    message = Message(subject="Confirm your account")
    message.recipients = ["{}".format(teacher.email)]

    send_mail_with_html(message,
                        'account_confirmation.html.j2',
                        confirmation_link=confirmation_link)


@celery.task
def send_account_recovery_instructions(email):
    teacher = Teacher.query.filter_by(email=email).first()
    try:
        recovery_link = teacher.get_reset_link()

        message = Message(subject="Recover your account")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html(message,
                            'account_confirmation.html.j2',
                            recovery_link=recovery_link)
    except Exception:
        # Ignore non-existing email addresses
        return
