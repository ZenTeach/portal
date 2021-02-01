from random import choice
from typing import Dict, List, Optional
from uuid import uuid4

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.api.class_quiz_api import ClassQuiz
from server.api.questions_api import Question
from server.lib import Grader
from server.lib.grader import CorrectChoice, Feedback
from server.models import (ClassQuizStatus, QuizGrade, QuizSession,
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
    st: Student = StudentFactory(classes=[school_class])
    st.add_to_class(school_class)
    return st


@pytest.fixture
def classquiz_(school_class: SchoolClass, client: FlaskClient) -> ClassQuiz:
    return school_class.quizzes[0]


@pytest.fixture
def quiz_session(student: Student, classquiz_: ClassQuiz, client: FlaskClient) -> QuizSession:
    # quiz = ClassQuizFactory.build(class_id=school_class.id)
    # quiz.save()
    return QuizSessionFactory(student_id=student.id,
                              class_quiz_id=classquiz_.id)


@pytest.fixture
def quizgrade_(student: Student, classquiz_: ClassQuiz, client: FlaskClient) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, score=None)


@pytest.fixture
def question_(client: FlaskClient) -> Question:
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
                               mocker: MockFixture):
        def _mock_grader_init(school_class_id: int, class_quiz: ClassQuiz, *args):
            assert school_class_id is not None
            assert class_quiz is not None

        mocker.patch('server.lib.grader.Grader.__init__', _mock_grader_init)
        mocker.patch('server.lib.grader.Grader.start_grading')
        mocker.patch('server.lib.grader.Feedback')

        Grader.from_quiz_session(quiz_session.uuid)

    def test_from_quiz_session_without_session_raise_exception(self,
                                                               client: FlaskClient,
                                                               mocker: MockFixture
                                                               ):

        mocker.patch('server.lib.grader.Grader.start_grading')
        mocker.patch('server.lib.grader.Feedback')

        with pytest.raises(Exception):
            Grader.from_quiz_session(uuid4())

    def test_start_grading(self,
                           quiz_session: QuizSession,
                           quizgrade_: QuizGrade,
                           classquiz_: ClassQuiz,
                           response: List[Dict],
                           mocker: MockFixture):

        quizgrade_.responses = response
        quizgrade_.save()

        mocker.patch('server.lib.grader.Feedback')

        @mocker.patch('server.lib.grader.Grader._score_quiz')
        def start_grading_assertions(_score_quiz):
            Grader.from_quiz_session(quiz_session.uuid)

            _score_quiz.assert_called_with(response, classquiz_)

    def test__score_quiz(self,
                         quiz_session: QuizSession,
                         quizgrade_: QuizGrade,
                         classquiz_: ClassQuiz,
                         response: List[Dict],
                         mocker: MockFixture):

        quizgrade_.responses = response
        quizgrade_.save()

        mocker.patch('server.lib.grader.Feedback')

        @mocker.patch('server.lib.grader.Grader._score_quiz')
        def start_grading_assertions(_score_quiz):
            Grader.from_quiz_session(quiz_session.uuid)

            _score_quiz.assert_called_with(response, classquiz_)

    def test__score_quiz_call_arguments(self,
                                        quiz_session: QuizSession,
                                        quizgrade_: QuizGrade,
                                        classquiz_: ClassQuiz,
                                        response: List[Dict],
                                        mocker: MockFixture):

        quizgrade_.responses = response
        quizgrade_.save()

        mocker.patch('server.lib.grader.Feedback')

        @mocker.patch('server.lib.grader.Grader._score_quiz')
        def _mock__score_quiz(quiz_submissions: List[QuizGrade], class_quiz: ClassQuiz):
            assert isinstance(quiz_submissions[0], QuizGrade)
            assert quiz_submissions[0] == quizgrade_
            assert class_quiz is not None
            assert class_quiz == classquiz_
        Grader.from_quiz_session(quiz_session.uuid)

    def test__score_quiz_score_calculation_and_updates(self,
                                                       quiz_session: QuizSession,
                                                       quizgrade_: QuizGrade,
                                                       classquiz_: ClassQuiz,
                                                       response: List[Dict],
                                                       mocker: MockFixture):

        quizgrade_.responses = response
        quizgrade_.save()

        def _calculate_score_mock(instance,
                                  correct_responses: List['CorrectChoice'],
                                  submitted_response: List[Dict]):
            assert isinstance(correct_responses, list)
            assert isinstance(correct_responses[0], CorrectChoice)
            assert isinstance(submitted_response, list)
            assert isinstance(submitted_response[0], dict)

        mocker.patch('server.lib.grader.Feedback')
        mocker.patch('server.lib.grader.Feedback.build_from_question_id')
        mocker.patch('server.lib.grader.Grader._get_correct_choice_by_question_id')
        mocker.patch('server.lib.grader.Grader._calculate_score', _calculate_score_mock)
        mocker.patch('server.models.quiz_grade.QuizGrade.update_score')
        mocker.patch('server.models.quiz_grade.QuizGrade.is_graded')
        mocker.patch('server.models.quiz_grade.QuizGrade.update_grade_breakdown')

        Grader.from_quiz_session(quiz_session.uuid)

    def test__calculate_score(self,
                              quiz_session: QuizSession,
                              quizgrade_: QuizGrade,
                              classquiz_: ClassQuiz,
                              response: List[Dict],
                              mocker: MockFixture):
        quizgrade_.responses = response
        quizgrade_.save()

        def _mock_get_correct_choice_by_question_id(instance,
                                                    target: str,
                                                    stack: Optional[List[CorrectChoice]]):
            assert target
            assert stack

        mocker.patch('server.lib.grader.Feedback')
        mocker.patch('server.lib.grader.Feedback.build_from_question_id')
        mocker.patch('server.lib.grader.Grader._get_correct_choice_by_question_id')
        mocker.patch('server.lib.grader.Grader._calculate_score',
                     _mock_get_correct_choice_by_question_id)
        mocker.patch('server.models.quiz_grade.QuizGrade.update_score')
        mocker.patch('server.models.quiz_grade.QuizGrade.is_graded')
        mocker.patch('server.models.quiz_grade.QuizGrade.update_grade_breakdown')

        Grader.from_quiz_session(quiz_session.uuid)

    def test_grading_with_valid_response(self,
                                         quiz_session: QuizSession,
                                         quizgrade_: QuizGrade,
                                         classquiz_: ClassQuiz,
                                         response: List[Dict],
                                         mocker: MockFixture):
        quizgrade_.responses = response
        quizgrade_.save()

        Grader.from_quiz_session(quiz_session.uuid)
        assert quizgrade_.score is not None or quizgrade_.score != 0
        assert quizgrade_.graded
        assert quizgrade_.grade_breakdown is not None and len(quizgrade_.grade_breakdown) != 0


class TestFeedbackBuilder(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_build_from_question_id(self, question_: Question) -> None:
        builder = Feedback()
        for _choice in question_.choices:
            builder.build_from_question_id(question_.id, _choice.uuid)

        assert len(builder.feedback) == 1
        assert len(builder.feedback[0].keys()) == 4
        assert [*builder.feedback[0]] == ['topic', 'knowledge_item', 'progress', 'feedback']

    def test__get_topic_breakdown(self, question_: Question, mocker: MockFixture) -> None:
        builder = Feedback()

        @mocker.patch('server.lib.grader.Feedback._get_topic_breakdown')
        def _mock_get_topic_breakdown(self, topic):
            assert topic == question_.topic

        builder.build_from_question_id(question_.id, question_.choices[0].uuid)

    def test_compute_progress_for_topic(self, question_: Question, mocker: MockFixture) -> None:
        builder = Feedback()

        @mocker.patch('server.lib.grader.Feedback.compute_progress_for_topic')
        def _mock_compute_progress_for_topic(self, topic):
            assert topic == question_.topic

            assert self._get_topic_breakdown(topic)
        builder.build_from_question_id(question_.id, question_.choices[0].uuid)

    def test_compute_progress_for_topic_sets_progress(self,
                                                      question_: Question,
                                                      mocker: MockFixture) -> None:
        builder = Feedback()

        mocker.patch('server.lib.grader.Feedback.add_ki_to_topic')
        mocker.patch('server.lib.grader.Feedback.add_feedback_to_topic')
        builder.build_from_question_id(question_.id, question_.choices[0].uuid)

        # TODO: Add more cases here
        assert builder.feedback[0]['progress'] == ['0/1']

    def test_compute_progress_for_topic_exception(self,
                                                  question_: Question,
                                                  mocker: MockFixture) -> None:
        builder = Feedback()
        mocker.patch('server.lib.grader.Feedback._get_topic_breakdown', return_value=None)

        @mocker.patch('server.lib.grader.Feedback.compute_progress_for_topic')
        def _mock_compute_progress_for_topic(self, topic):
            assert topic == question_.topic

            assert self._get_topic_breakdown(topic)

        builder.build_from_question_id(question_.id, question_.choices[0].uuid)
