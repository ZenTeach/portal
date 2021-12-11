import os
from uuid import UUID

from celery.utils.log import get_task_logger
from flask_mail import Message
from server import celery
from server.lib import ReportCardGenerator
from server.lib.generators.report_card_generator import ModelNotFound
from server.models import QuizGrade

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

    except ModelNotFound as exc:
        logger.error(exc)
        raise
    except Exception as exc:
        logger.error(exc)
        raise self.retry(exc=exc, countdown=60)

    return generator.report_file_name
