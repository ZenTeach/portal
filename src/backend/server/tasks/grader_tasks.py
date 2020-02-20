from server import celery, db
from server.models import ClassQuiz, Student, ClassQuizStatus
from server.lib import Grader
#from flask_mail import Message
from celery.utils.log import get_task_logger
import asyncio

from .commons import send_mail, send_mail_with_html

logger = get_task_logger(__name__)

@celery.task
async def grader_administered_quizzes(quiz_session_id):
    try:
        Grader.from_quiz_session()
        # grader.start_grading()
    except Exception as e:
        print(e)

@celery.task
async def check_all_quizzes_submitted():
    """
        Periodically check if all the students submitted their quiz
        by checking ig no. of submissions == no. of students

        TODO: Next step for this task would be to used MATERIALIZED VIEWS
        with triggers to reduce the number of reads.
    """
    # Find the active quiz, i.e in created state
    # TODO: Needs to be fixed
    active_class_quiz = ClassQuiz.query\
                        .with_entities(ClassQuiz.id)\
                        .filter(status=ClassQuizStatus.created)
    # Execute a query against database
