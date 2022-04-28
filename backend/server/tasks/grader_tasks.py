from celery.utils.log import get_task_logger
from server import celery
from server.lib import Grader
from server.models import (ClassQuiz, ClassQuizStatus, QuizGrade, QuizSession,
                           QuizSessionStatus)

logger = get_task_logger(__name__)


@celery.task(bind=True)
def grader_administered_quizzes(self, quiz_session_id):
    try:
        logger.debug(f"grader_administered_quizzes: {quiz_session_id}")
        Grader.from_quiz_session(quiz_session_id)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(bind=True)
def grade_all_administered_quizzes(self):
    """
    Grades all quizzes that are currently being administered.
    """
    logger.info("Grading all administered quizzes")
    ended_sessions = QuizSession.query.filter_by(
        status=QuizSessionStatus.ended).all()
    for session in ended_sessions:
        celery.send_task('server.tasks.grader_tasks.grader_administered_quizzes',
                         args=[session.uuid])


@celery.task(bind=True)
def check_all_quizzes_administered(self):
    """
        Periodically check if all the students submitted their quiz
        by checking ig no. of submissions == no. of students

        TODO: Next step for this task would be to used MATERIALIZED VIEWS
        with triggers to reduce the number of reads.
    """
    try:
        # Find the active quiz, i.e in created state
        quizzes = ClassQuiz.query.filter_by(status=ClassQuizStatus.created).all()
        logger.info(f"Checking {len(quizzes)} created quizzes")
        for quiz in quizzes:
            # Find the students who have submitted the quiz
            students = quiz.school_class.students
            # Find the students who have not submitted the quiz
            completed_quiz_sessions = QuizSession.query.filter_by(
                class_quiz_id=quiz.id, status=QuizSessionStatus.ended).count()
            # Check if the no. of students == no. of completed quiz sessions
            if len(students) == completed_quiz_sessions:
                quiz.update_and_save(status=ClassQuizStatus.administered)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(bind=True)
def check_all_quizzes_graded(self):
    """
        Periodically check if all the students submitted their quiz
        by checking ig no. of submissions == no. of students

        TODO: Next step for this task would be to used MATERIALIZED VIEWS
        with triggers to reduce the number of reads.
    """
    try:
        # Find the active quiz, i.e in created state
        quizzes = ClassQuiz.query.filter_by(status=ClassQuizStatus.created).all()
        logger.info(f"Checking {len(quizzes)} created quizzes")
        for quiz in quizzes:
            # Find the students who have submitted the quiz
            students = quiz.school_class.students
            # Find the students who have not submitted the quiz
            graded_quizzes = QuizGrade.query.filter_by(class_quiz_id=quiz.id, graded=True).count()
            # Check if the no. of students == no. of completed quiz sessions
            if len(students) == graded_quizzes:
                quiz.update_and_save(status=ClassQuizStatus.graded)
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)


@celery.task(bind=True)
def regrade_quiz(self, quiz_id: int, student_id: int):
    try:
        Grader.from_student_and_quiz_id(student_id, quiz_id)
    except ValueError as e:
        raise e
    except Exception as e:
        logger.error(e)
        self.retry(exc=e, countdown=2 ** self.request.retries)
