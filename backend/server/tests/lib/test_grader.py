from random import choice
from typing import Dict, List, Optional, Tuple
from uuid import UUID

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.api.class_quiz_api import ClassQuiz
from server.lib import Grader
from server.lib.grader import CorrectChoice, Feedback
from server.models import (ClassQuizStatus, KnowledgeItem, Questions,
                           QuizGrade, QuizSession, SchoolClass, Student,
                           Subject, Teacher, Topic)
from server.models.question_choice import QuestionChoice
from server.tests.factories import (KnowledgeItemFactory, QuestionsFactory,
                                    QuizGradeFactory, QuizSessionFactory,
                                    SchoolClassFactory, StudentFactory,
                                    TopicFactory)


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def school_class(teacher_: Teacher, client: FlaskClient) -> SchoolClass:
    return SchoolClassFactory(teacher_id=teacher_.id, with_classquiz=ClassQuizStatus.administered)


@pytest.fixture
def student(school_class: SchoolClass, client: FlaskClient) -> Student:
    st: Student = StudentFactory.create(classes=[school_class])
    st.add_to_class(school_class)
    return st


@pytest.fixture
def subject_() -> Subject:
    subject = Subject(name='Physics', enabled=True)
    subject.save()
    return subject


@pytest.fixture
def topic_(subject_: Subject) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def knowledge_items_(topic_: Topic, subject_: Subject) -> List[KnowledgeItem]:
    return [KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id) for _ in range(5)]


@pytest.fixture
def knowledge_item_(topic_: Topic, subject_: Subject) -> KnowledgeItem:
    return KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id)


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
def question_(client: FlaskClient,
              knowledge_item_: KnowledgeItem,
              topic_: Topic) -> Questions:
    return QuestionsFactory.create(multiple_choice_question_type=True,
                                   knowledge_item=knowledge_item_,
                                   topic=topic_,
                                   with_choices={
                                       'choice_count': 4,
                                       'choice_weight': 1,
                                   })


@pytest.fixture(autouse=True)
def questions_(client: FlaskClient,
               topic_: Topic,
               knowledge_items_: List[KnowledgeItem]) -> None:
    questions = []
    for knowledge_item in knowledge_items_:
        questions.extend(QuestionsFactory.create_batch(2,
                                                       multiple_choice_question_type=True,
                                                       knowledge_item=knowledge_item,
                                                       topic=topic_,
                                                       with_choices={
                                                           'choice_count': 4,
                                                           'choice_weight': 1,
                                                       })
                         )


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


def test_from_quiz_session(quiz_session: QuizSession,
                           school_class: SchoolClass,
                           mocker: MockFixture):
    def _mock_grader_init(school_class_id: int, class_quiz: ClassQuiz, *args):
        assert school_class_id is not None
        assert class_quiz is not None

    mocker.patch('server.lib.grader.Grader.__init__', _mock_grader_init)
    mocker.patch('server.lib.grader.Grader.start_grading')
    mocker.patch('server.lib.grader.Feedback')

    Grader.from_quiz_session(quiz_session.uuid)


def test_start_grading(quiz_session: QuizSession,
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


def test__score_quiz(quiz_session: QuizSession,
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


def test__score_quiz_call_arguments(quiz_session: QuizSession,
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


def test__score_quiz_score_calculation_and_updates(quiz_session: QuizSession,
                                                   quizgrade_: QuizGrade,
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


def test__get_correct_choice_by_question_id(quiz_session: QuizSession,
                                            quizgrade_: QuizGrade,
                                            response: List[Dict],
                                            mocker: MockFixture):
    quizgrade_.response = response
    quizgrade_.save()

    def _mock_get_correct_choice_by_question_id(instance,
                                                target: UUID,
                                                stack: Optional[List[CorrectChoice]]):
        assert isinstance(target, UUID)
        assert stack


def test__calculate_score(quiz_session: QuizSession,
                          quizgrade_: QuizGrade,
                          response: List[Dict],
                          mocker: MockFixture):
    quizgrade_.responses = response
    quizgrade_.save()

    def _mock_get_correct_choice_by_question_id(instance,
                                                target: UUID,
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


def test_grading_with_valid_response(quiz_session: QuizSession,
                                     quizgrade_: QuizGrade,
                                     response: List[Dict]):
    quizgrade_.responses = response
    quizgrade_.save()

    Grader.from_quiz_session(quiz_session.uuid)
    assert quizgrade_.score is not None or quizgrade_.score != 0
    assert quizgrade_.graded
    assert quizgrade_.grade_breakdown is not None and len(quizgrade_.grade_breakdown) != 0


@pytest.fixture
def question_topic_and_ki(client: FlaskClient) -> Tuple[str, str]:
    q = Questions.query.first()
    return (q.topic.value, q.knowledge_item.value)


@pytest.fixture
def ki_q_count(client: FlaskClient, question_topic_and_ki: Tuple[str, str]) -> dict:
    return {
        question_topic_and_ki[1]: 1
    }


@pytest.fixture
def choice_feedback(client: FlaskClient) -> str:
    return QuestionChoice.query.first().feedback


class TestFeedbackBuilder(object):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_build_from_question_id(self,
                                    question_topic_and_ki: Tuple[str, str],
                                    choice_feedback: str) -> None:
        builder = Feedback()

        builder.build_from_question_id(question_topic_and_ki, choice_feedback, False, {})

        assert len(builder.feedback) == 1
        assert len(builder.feedback[0].keys()) == 1
        assert [*builder.feedback[0].keys()] == [question_topic_and_ki[0]]
        assert [*builder.feedback[0]
                [question_topic_and_ki[0]].keys()] == [question_topic_and_ki[1]]
        assert [*builder.feedback[0][question_topic_and_ki[0]]
                [question_topic_and_ki[1]].keys()] == ['feedback', 'progress']

    def test__get_topic_breakdown(self,
                                  question_topic_and_ki: Tuple[str, str]) -> None:
        builder = Feedback()
        builder.build_for_topic(question_topic_and_ki[0])
        assert builder._get_topic_breakdown(question_topic_and_ki[0])

    def test_compute_progress_for_correct_response(self,
                                                   question_topic_and_ki: Tuple[str, str],
                                                   choice_feedback: str,
                                                   ki_q_count: dict) -> None:
        builder = Feedback()
        builder.build_from_question_id(question_topic_and_ki, choice_feedback, True, ki_q_count)
        assert builder.feedback[0][question_topic_and_ki[0]
                                   ][question_topic_and_ki[1]]['progress'] == '1/1'

    def test_compute_progress_for_incorrect_response(self,
                                                     question_topic_and_ki: Tuple[str, str],
                                                     choice_feedback: str,
                                                     ki_q_count: dict) -> None:
        builder = Feedback()
        builder.build_from_question_id(question_topic_and_ki, choice_feedback, False, ki_q_count)

        assert builder.feedback[0][question_topic_and_ki[0]
                                   ][question_topic_and_ki[1]]['progress'] == '0/1'

    def test_response_feedback_when_incorrectly_answered(self,
                                                         question_topic_and_ki: Tuple[str, str],
                                                         choice_feedback: str):
        builder = Feedback()
        builder.build_from_question_id(question_topic_and_ki, choice_feedback, False, {})

        assert [*builder.feedback[0][question_topic_and_ki[0]]
                [question_topic_and_ki[1]]['feedback']] == [choice_feedback]

    def test_response_feedback_when_correctly_answered(self,
                                                       question_topic_and_ki: Tuple[str, str],
                                                       choice_feedback: str):
        another_builder = Feedback()
        another_builder.build_from_question_id(question_topic_and_ki, choice_feedback, True, {})
        assert [*another_builder.feedback[0][question_topic_and_ki[0]]
                [question_topic_and_ki[1]]['feedback']] == []

    def test_generated_feedback_structure(self,
                                          question_topic_and_ki: Tuple[str, str],
                                          ki_q_count: dict,
                                          choice_feedback: str) -> None:
        builder = Feedback()
        builder.build_from_question_id(question_topic_and_ki, choice_feedback, False, ki_q_count)

        assert builder.feedback == [{
            question_topic_and_ki[0]: {
                question_topic_and_ki[1]: {
                    "progress": "0/1",
                    "feedback": [choice_feedback],
                }
            }
        }]
