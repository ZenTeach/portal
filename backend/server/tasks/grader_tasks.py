from celery.utils.log import get_task_logger
from server import celery
from server.lib import Grader
from server.models import ClassQuiz, ClassQuizStatus, QuizGrade, QuizSession

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
    active_class_quiz = ClassQuiz.query.with_entities(ClassQuiz.id).filter(  # noqa
        status=ClassQuizStatus.created
    )
    # Execute a query against database


@celery.task
def regrade_quiz(quiz_id: int, student_id: int):
    quiz_grade = QuizGrade.query.filter_by(student_id=student_id, class_quiz_id=quiz_id).first()
    quiz_session = QuizSession.query.filter_by(
        student_id=student_id, class_quiz_id=quiz_id).first()

    if quiz_grade is None:
        return

    if quiz_session is None:
        return

    quiz_grade.prepare_regrade_()

    grader_administered_quizzes.delay(quiz_session.uuid)
