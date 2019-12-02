from server import celery
from server.lib import QuizGenerator
from server import mail
from flask_mail import Message
from celery.contrib import rdb


@celery.task
def generate_pdf(quiz_id):
    generator = QuizGenerator("/home/flask/server/server/api/templates",
                                  "demo.html",
                                  "/tmp/zenteach_quizzes")
    # rdb.set_trace()
    try:
        generator.generate(quiz_id)
    except Exception as e:
        print(e)

    return generator.quiz_file_name

@celery.task
def send_quiz_pdf(teacher_email, quiz_file_dir):
    msg = Message(subject="Hi! Your Quiz have arrived.")
    msg.recipients=["{}".format(teacher_email)]

    with open(quiz_file_dir, 'rb') as fp:
        msg.attach("Quiz.pdf", "application/pdf", fp.read())

    mail.send(msg)
