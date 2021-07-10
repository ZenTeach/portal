from server.models import QuizGrade
from server.tasks import regrade_quiz


def trigger_quiz_regrading():
    for quiz_grade in QuizGrade.query.all():
        # enqueue regrade_quiz jobs for all quiz grades
        regrade_quiz(quiz_grade.class_quiz_id, quiz_grade.student_id)
