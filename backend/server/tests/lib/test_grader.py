from random import choice
from typing import Dict, List

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.api.class_quiz_api import ClassQuiz
from server.lib import Grader
from server.models import (ClassQuizStatus, Questions, QuizGrade, QuizSession,
                           SchoolClass, Student, Teacher)
from server.tests.factories import (QuestionsFactory, QuizGradeFactory,
                                    QuizSessionFactory, SchoolClassFactory,
                                    StudentFactory, TeacherFactory)


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def school_class(teacher_: Teacher, client: FlaskClient) -> SchoolClass:
    return SchoolClassFactory(teacher_id=teacher_.id, with_classquiz=ClassQuizStatus.administered)


@pytest.fixture
def student(school_class: SchoolClass, client: FlaskClient) -> Student:
    st: Student = StudentFactory.create(classes=[school_class])
    st.add_to_class(school_class)
    return st


@pytest.fixture
def classquiz_(school_class: SchoolClass, client: FlaskClient) -> ClassQuiz:
    return school_class.quizzes[0]


@pytest.fixture(scope='function')
def quiz_session(student: Student, classquiz_: ClassQuiz, client: FlaskClient) -> QuizSession:
    return QuizSessionFactory(student_id=student.id,
                              class_quiz_id=classquiz_.id)


@pytest.fixture
def quizgrade_(student: Student, classquiz_: ClassQuiz, client: FlaskClient) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, score=None)


@pytest.fixture
def question_(client: FlaskClient) -> Questions:
    return QuestionsFactory.create(multiple_choice_question_type=True, with_choices=4)


@pytest.fixture
def response(classquiz_: ClassQuiz, client: FlaskClient) -> List[Dict]:
    """
        QuizGrade.response is an array of dict
        [{
            questionID: qId,
            Choice_answer: a
        }]
    """

    return [
        {
            'questionID': question['id'],
            'Choice_answer': choice(question['choices'])['uuid']
        }
        for question in classquiz_.questions
    ]


class TestQuizGrader(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_from_quiz_session(self,
                               quiz_session: QuizSession,
                               school_class: SchoolClass,
                               mocker: MockFixture):
        def _mock_grader_init(school_class_id: int, class_quiz: ClassQuiz, *args):
            assert school_class_id is not None
            assert class_quiz is not None

        mocker.patch('server.lib.grader.Grader.__init__', _mock_grader_init)
        mocker.patch('server.lib.grader.Grader.start_grading')
        mocker.patch('server.lib.grader.Feedback')

        Grader.from_quiz_session(quiz_session.uuid)
