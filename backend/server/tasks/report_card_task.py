import os
from uuid import UUID

from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.lib import ReportCardGenerator
from server.lib.generators.report_card_generator import ModelNotFound
from server.models import ClassQuiz, QuizGrade

from .commons import send_mail_with_html

logger = get_task_logger(__name__)


@celery.task(bind=True)
def send_report_card_pdf(self, report_card_id: UUID):
    generator = None
    grade = QuizGrade.query.filter_by(uuid=report_card_id).first()

    if grade is None:
        return

    try:
        template_directory = f"{os.getenv('TEMPLATE_DIR')}/api"
        generator = ReportCardGenerator(
            template_directory,
            "report_card_template.html",
            "/tmp/zenteach_quizzes"   # nosec
        )
        generator.generate(report_card_id)

        msg = Message(subject="Hi! Your Report Card PDF has arrived")
        msg.recipients = ["{}".format(grade.student.email)]

        with open(generator.report_file_name, 'rb') as fp:
            msg.attach("ReportCard.pdf", "application/pdf", fp.read())

        send_mail_with_html(msg, "report_card.html.j2",
                            full_name=grade.student.full_name)
        grade.update_save(result_sent=True)
    except ModelNotFound as exc:
        logger.error(exc)
        raise
    except Exception as exc:
        logger.error(exc)
        raise self.retry(exc=exc, countdown=2**self.request.retries)

    return generator.report_file_name


@celery.task(bind=True)
def send_graded_quizzes(self):
    # TODO: Remove public-class quiz filter
    unsent_graded_quizzes = QuizGrade.query.join(ClassQuiz).filter(
        ClassQuiz.private == False).filter_by(  # noqa
            graded=True, result_sent=False
    ).all()
    for unsent_report_card in unsent_graded_quizzes:
        celery.send_task('server.tasks.report_card_task.send_report_card_pdf',
                         args=[unsent_report_card.uuid])
