import pytest
from flask.testing import FlaskClient
from server.models import (KnowledgeItem, QuestionChoice, Questions, Subject,
                           Topic)
from server.tests.factories import (KnowledgeItemFactory,
                                    QuestionChoiceFactory, QuestionsFactory,
                                    TopicFactory)


@pytest.fixture
def question_choice() -> QuestionChoice:
    q_id = Questions.query.first().id
    return QuestionChoiceFactory(question=q_id)


@pytest.fixture
def subject_() -> Subject:
    s = Subject(name="Chemistry", enabled=True)
    s.save()
    return s


@pytest.fixture
def topic_(subject_: Subject) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def knowledge_item(client: FlaskClient,
                   subject_: Subject,
                   topic_: Topic) -> KnowledgeItem:
    return KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id)


@pytest.fixture(autouse=True)
def questions(client: FlaskClient, knowledge_item: KnowledgeItem, topic_: Topic) -> None:
    QuestionsFactory.create_batch(5,
                                  knowledge_item=knowledge_item,
                                  topic=topic_,
                                  multiple_choice_question_type=True, with_choices=4)


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
