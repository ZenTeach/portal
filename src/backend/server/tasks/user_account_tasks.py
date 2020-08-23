from flask_mail import Message
from server import celery
from server.models import Teacher
from server.tasks.commons import send_mail_with_html


@celery.task
def confirm_user(teacher_id):
    teacher = Teacher.query.find(teacher_id)
    if not teacher:
        raise Exception('Teacher not found')

    return teacher.confirm_user()


@celery.task
def send_confirmation_instructions(teacher_id):
    teacher = Teacher.query.find(teacher_id)
    confirmation_link = teacher.generate_confirmation_link()

    message = Message(subject="Confirm your account")
    message.recipients = ["{}".format(teacher.email)]

    send_mail_with_html(message,
                        'account_confirmation.html.j2',
                        confirmation_link=confirmation_link)


def confirm_and_send_instruction(teacher_id):
    chain = confirm_user(teacher_id) | send_confirmation_instructions.s()
    chain()
