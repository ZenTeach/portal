from celery import current_app
from celery.utils.log import get_task_logger
from server.lib import Summarizer
from server.models import Teacher

logger = get_task_logger(__name__)
celery = current_app


@celery.task(bind=True)
def enqueue_summary_for_teacher(self, days_before: int):
    try:
        for teacher in Teacher.query.all():

            logger.debug(f'Calling summarizer for teacher {teacher}')
            s = Summarizer(teacher)
            s(days_before)
            logger.debug('Finished summarizer')
        return None
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)
