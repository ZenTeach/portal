from celery import current_app
from celery.utils.log import get_task_logger
from flask_mail import Message
from server.models import ClassQuiz, Teacher

from .commons import send_mail_with_html

logger = get_task_logger(__name__)
celery = current_app


@celery.task(bind=True, default_retry_delay=1 * 60)
def send_quiz_generation_email(self, teacher_email, quiz_id):
    try:
        msg = Message(subject="Hi! Your Quiz has arrived.")
        msg.recipients = ["{}".format(teacher_email)]
        quiz = ClassQuiz.query.filter_by(id=quiz_id).first()
        teacher_fullname = Teacher.query.filter_by(email=teacher_email).first().full_name()
        send_mail_with_html(msg, "class_quiz_prepared.html.j2",
                            full_name=teacher_fullname, quiz_link=quiz.url)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
