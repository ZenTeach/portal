
from pathlib import Path

from celery.utils.log import get_task_logger
from flask_mail import Message
from server import app, celery
from server.lib import QuizGenerator
from server.models import ClassQuiz, Teacher

from .commons import send_mail, send_mail_with_html

logger = get_task_logger(__name__)


@celery.task
def generate_pdf(quiz_id):
    template_directory = Path(app.root_path)\
        .joinpath(app.template_folder)\
        .joinpath('/api')
    generator = QuizGenerator(
        "{}".format(template_directory),
        "demo.html",
        "/tmp/zenteach_quizzes"   # nosec
    )
    try:
        generator.generate(quiz_id)
    except Exception as e:
        print(e)

    return generator.quiz_file_name


@celery.task
def send_quiz_generation_email(teacher_email, quiz_id):
    msg = Message(subject="Hi! Your Quiz have arrived.")
    msg.recipients = ["{}".format(teacher_email)]
    quiz = ClassQuiz.query.filter_by(id=quiz_id).first()
    teacher_fullname = Teacher.query.filter_by(email=teacher_email).first().full_name()
    send_mail_with_html(msg, "class_quiz_prepared.html.j2",
                        full_name=teacher_fullname, quiz_link=quiz.url)


@celery.task
def send_quiz_pdf(teacher_email, quiz_file_dir):
    msg = Message(subject="Hi! Your Quiz have arrived.")
    msg.recipients = ["{}".format(teacher_email)]

    with open(quiz_file_dir, "rb") as fp:
        msg.attach("Quiz.pdf", "application/pdf", fp.read())

    send_mail(msg)
