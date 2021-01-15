import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.api.class_quiz_api import ClassQuiz
from server.lib import Grader
from server.models import QuizSession, SchoolClass, Student, Teacher
from server.tests.factories import (ClassQuizFactory, SchoolClassFactory,
                                    StudentFactory, TeacherFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    st: Student = StudentFactory.create(classes=[school_class])
    st.add_to_class(school_class)
    return st


@pytest.fixture(scope='function')
def quiz_session(school_class: SchoolClass, student: Student) -> QuizSession:
    quiz = ClassQuizFactory.build(class_id=school_class.id)
    quiz.save()


def quiz_submission():
    pass


class TestQuizGrader(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    @pytest.mark.skip
    def test_from_quiz_session(self, client: FlaskClient,
                               quiz_session: QuizSession,
                               school_class: SchoolClass,
                               mocker: MockFixture):
        def _mock_grader_init(school_class_id: int, class_quiz: ClassQuiz):
            assert school_class_id is not None
            assert class_quiz is not None

        mocker.patch('server.lib.grader.Grader.__init__', _mock_grader_init)
        mocker.patch('server.lib.grader.Grader.start_grading')
        mocker.patch('server.lib.grader.Feedback')

        Grader.from_quiz_session(quiz_session.uuid)

    def test_quiz_grading(self, client: FlaskClient,
                          quiz_session: QuizSession,
                          school_class: SchoolClass,
                          mocker: MockFixture):
        pass
