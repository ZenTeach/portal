from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.models import Student
from server.tasks.commons import send_mail_with_html

logger = get_task_logger(__name__)


@celery.task(bind=True)
def send_student_confirmation_instructions(self, student_id):
    try:
        student = Student.query.filter_by(id=student_id).first()
        confirmation_link = student.generate_confirmation_link('/confirm_student_account')

        message = Message(subject="Confirm your account!")
        message.recipients = ["{}".format(student.email)]

        send_mail_with_html(message,
                            'student_confirmation.html.j2',
                            confirmation_link=confirmation_link)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)
