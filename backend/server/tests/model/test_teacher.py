import pytest
from flask.testing import FlaskClient
from server.models import KnowledgeItem, Questions, Subject, Teacher, Topic
from server.tests.factories import (KnowledgeItemFactory, QuestionsFactory,
                                    TopicFactory)


@pytest.fixture
def subject_() -> Subject:
    subject = Subject(name='Chemistry', enabled=True)
    subject.save()
    return subject


@pytest.fixture
def topic_(subject_: Subject) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def knowledge_item_(topic_: Topic, subject_: Subject) -> KnowledgeItem:
    return KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id)


@pytest.fixture
def questions_(subject_: Subject, topic_: Topic, knowledge_item_: KnowledgeItem) -> Questions:
    return QuestionsFactory(multiple_choice_question_type=True,
                            topic=topic_,
                            knowledge_item=knowledge_item_,
                            with_choices=4)


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


def test_teacher_model(client: FlaskClient):
    assert Teacher.query.first()


def test_teacher_confirmable(client: FlaskClient):
    teacher = Teacher.query.first()

    assert teacher.confirmed == False  # noqa
    assert teacher.confirmed_at is None
    assert teacher.confirmation_token is None


def test_teacher_add_question(client: FlaskClient,
                              teacher_: Teacher,
                              questions_: Questions):
    teacher_.questions.append(questions_)

    assert teacher_.questions[0] == questions_
    assert questions_.teacher_id == teacher_.id


def test_teacher_remove_question(client: FlaskClient,
                                 teacher_: Teacher,
                                 questions_: Questions):
    questions_.teacher_id = teacher_.id
    questions_.save()
    teacher_.reload()

    teacher_.questions.pop()
    questions_.reload()

    assert teacher_.questions == []
    assert questions_.teacher_id is None
