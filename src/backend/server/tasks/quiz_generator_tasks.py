
from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.lib import QuizGenerator

from .commons import send_mail, send_mail_with_html

logger = get_task_logger(__name__)


@celery.task
def generate_pdf(quiz_id):
    generator = QuizGenerator(
        "/home/flask/server/server/api/templates",
        "demo.html",
        "/tmp/zenteach_quizzes"   # nosec
    )
    try:
        generator.generate(quiz_id)
    except Exception as e:
        print(e)

    return generator.quiz_file_name


@celery.task
def send_google_form_email(teacher_email, published_url):
    msg = Message(subject="Your Google Form quiz is ready!")
    msg.recipients = ["{}".format(teacher_email)]

    # msg.body = "Hi,\n Your Google Form can be
    # found by following this link: {}\n
    # \nThank you for using zenteach,\n \nZenteach support"
    # .format(published_url)
    send_mail_with_html(msg, "google_form_template.html",
                        form_link=published_url)
    # send_mail(msg)


@celery.task
def send_quiz_pdf(teacher_email, quiz_file_dir):
    msg = Message(subject="Hi! Your Quiz have arrived.")
    msg.recipients = ["{}".format(teacher_email)]

    with open(quiz_file_dir, "rb") as fp:
        msg.attach("Quiz.pdf", "application/pdf", fp.read())

    send_mail(msg)
