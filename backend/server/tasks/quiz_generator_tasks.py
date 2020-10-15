
import os
from pathlib import Path

from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.lib import QuizGenerator
from server.models import ClassQuiz, Teacher

from .commons import send_mail, send_mail_with_html

logger = get_task_logger(__name__)


@celery.task(bind=True)
def generate_pdf(self, quiz_id):
    generator = None
    try:
        template_directory = Path(os.getenv('TEMPLATE_DIR'))\
            .joinpath('/api')
        generator = QuizGenerator(
            "{}".format(template_directory),
            "demo.html",
            "/tmp/zenteach_quizzes"   # nosec
        )
        generator.generate(quiz_id)
    except Exception as exc:
        logger.error(exc)
        raise self.retry(exc=exc, countdown=60)

    return generator.quiz_file_name


@celery.task(bind=True, default_retry_delay=1 * 60)
def send_quiz_generation_email(self, teacher_email, quiz_id):
    try:
        msg = Message(subject="Hi! Your Quiz have arrived.")
        msg.recipients = ["{}".format(teacher_email)]
        quiz = ClassQuiz.query.filter_by(id=quiz_id).first()
        teacher_fullname = Teacher.query.filter_by(email=teacher_email).first().full_name()
        send_mail_with_html(msg, "class_quiz_prepared.html.j2",
                            full_name=teacher_fullname, quiz_link=quiz.url)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery.task(bind=True)
def send_quiz_pdf(self, teacher_email, quiz_file_dir):
    try:
        msg = Message(subject="Hi! Your Quiz PDF have arrived.")
        msg.recipients = ["{}".format(teacher_email)]

        with open(quiz_file_dir, "rb") as fp:
            msg.attach("Quiz.pdf", "application/pdf", fp.read())

        send_mail(msg)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
