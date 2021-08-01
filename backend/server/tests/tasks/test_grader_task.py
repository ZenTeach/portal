import pytest
from flask.testing import FlaskClient
from pytest import fail
from pytest_mock import MockFixture
from server.lib.grader import Grader
from server.models import QuizGrade, QuizSession, QuizSessionStatus, Student
from server.models.class_quiz import ClassQuiz
from server.tasks.grader_tasks import grader_administered_quizzes, regrade_quiz
from server.tests.factories import (QuizGradeFactory, SchoolClassFactory,
                                    StudentFactory, TeacherFactory)


@pytest.fixture
def student_(client: FlaskClient) -> Student:
    return StudentFactory()


@pytest.fixture
def classquiz(client: FlaskClient) -> ClassQuiz:
    teacher = TeacherFactory()
    sc = SchoolClassFactory(with_classquiz=True, teacher_id=teacher.id)
    return sc.quizzes[0]


@pytest.fixture
def quiz_grade_(client: FlaskClient, student_: Student, classquiz: ClassQuiz):
    QuizSession(student_id=student_.id,
                class_quiz_id=classquiz.id,
                status=QuizSessionStatus.ended).save()

    return QuizGradeFactory(student_id=student_.id,
                            class_quiz_id=classquiz.id)


class TestQuizGraderTask:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_grader_administered_quizzes_runs(self, monkeypatch):
        def mock_from_quiz_session(x):
            return True
        monkeypatch.setattr(Grader, 'from_quiz_session', mock_from_quiz_session)
        try:
            grader_administered_quizzes('some_foo_id')
        except Exception as exception:
            raise fail("DID RAISE {0}".format(exception))

    def test_grader_regrade_quiz(self, monkeypatch,
                                 mocker: MockFixture,
                                 student_: Student,
                                 quiz_grade_: QuizGrade,
                                 classquiz: ClassQuiz):
        mocker.patch('server.tasks.grader_tasks.grader_administered_quizzes')

        @mocker.patch('server.models.QuizGrade.prepare_regrade_')
        def mocked_quiz_grade_method(prepare_regrade_mock):
            prepare_regrade_mock.assert_called()

        @mocker.patch('server.tasks.grader_tasks.regrade_quiz')
        def mocked_grader_tasks(regrade_quiz_mock):
            regrade_quiz_mock.assert_called_with(classquiz.id, student_.id)

        regrade_quiz(classquiz.id, student_.id)
