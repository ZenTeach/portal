import pytest
from flask.testing import FlaskClient
from server.models import QuestionChoice, Questions
from server.tests.factories import QuestionChoiceFactory, QuestionsFactory


@pytest.fixture
def question_choice() -> QuestionChoice:
    q_id = Questions.query.first().id
    return QuestionChoiceFactory(question=q_id)


@pytest.fixture(autouse=True)
def questions(client: FlaskClient) -> None:
    QuestionsFactory.create_batch(5, multiple_choice_question_type=True, with_choices=4)


@pytest.fixture
def another_choice() -> QuestionChoice:
    q_id = Questions.query.all()[2].id
    return QuestionChoiceFactory(question=q_id)


def test_question_choice_is_correct_choice(client: FlaskClient,
                                           question_choice: QuestionChoice) -> None:

    assert not question_choice.is_correct_choice
    question_choice.is_correct_choice = True
    assert question_choice.is_correct_choice


def test_question_choice_get_non_pk_columns(client: FlaskClient,
                                            question_choice: QuestionChoice) -> None:
    assert len(question_choice.get_non_pk_columns()) == 4
    assert sorted(question_choice.get_non_pk_columns()) == [
        'feedback', 'question_id', 'value', 'weight']


def test_question_choice_empty_instance(client: FlaskClient) -> None:
    empty_instance = QuestionChoice.empty_instance()

    assert empty_instance.value == ""


def test_question_choice_clone(client: FlaskClient,
                               question_choice: QuestionChoice) -> None:

    cloned = QuestionChoice.clone(question_choice)
    assert cloned.value == question_choice.value
    assert cloned.feedback == question_choice.feedback
    assert cloned.weight == question_choice.weight
    assert cloned.uuid != question_choice.uuid
    assert cloned.question_id == question_choice.question_id


def test_question_choice_clone_with_kwargs(client: FlaskClient,
                                           question_choice: QuestionChoice,
                                           another_choice: QuestionChoice) -> None:
    test_kwarg = {'value': 'some value'}
    cloned = QuestionChoice.clone(question_choice, **test_kwarg)
    assert cloned.value != question_choice.value

    test_kwarg = {'question_id': another_choice.question_id}
    cloned = QuestionChoice.clone(question_choice, **test_kwarg)
    assert cloned.question_id != question_choice.question_id
