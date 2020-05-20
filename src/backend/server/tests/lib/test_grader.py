import pytest
from server.lib.grader import Grader
from server.models import ClassQuizStatus, ClassQuiz, SchoolClass

def test_grader(client, teacher_factory):
    # TODO
    # teacher = teacher_factory(has_class_and_student=True)
    # school_class = teacher.classes[0]
    # class_quiz = school_class.quizzes[0]
    # school_class = SchoolClass.query.filter_by(teacher_id=teacher.id).first()
    # class_quiz = ClassQuiz.query.filter_by(class_id=school_class.id)
    # grader_test_object = Grader.from_quiz_session()
    assert True
    # assert class_quiz.status == ClassQuizStatus.created
