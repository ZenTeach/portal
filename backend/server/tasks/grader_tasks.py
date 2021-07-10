from celery.utils.log import get_task_logger
from server import celery
from server.lib import Grader

logger = get_task_logger(__name__)


@celery.task(bind=True)
def grader_administered_quizzes(self, quiz_session_id):
    try:
        Grader.from_quiz_session(quiz_session_id)
        # grader.start_grading()
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task
def check_all_quizzes_submitted():
    """
        Periodically check if all the students submitted their quiz
        by checking ig no. of submissions == no. of students

        TODO: Next step for this task would be to used MATERIALIZED VIEWS
        with triggers to reduce the number of reads.
    """
    # Find the active quiz, i.e in created state
    # TODO: Needs to be fixed
    # Execute a query against database


@celery.task(bind=True)
def regrade_quiz(self, quiz_id: int, student_id: int):
    try:
        Grader.from_student_and_quiz_id(student_id, quiz_id)
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)
