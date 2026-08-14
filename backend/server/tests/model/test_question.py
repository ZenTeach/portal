from typing import Dict, OrderedDict

import pytest
from factory import build
from flask.testing import FlaskClient
from pydantic import ValidationError
from server.models import KnowledgeItem, Questions, Subject, Topic
from server.tests.factories import QuestionsFactory, SubjectFactory
from server.tests.factories.knowledge_item_factory import KnowledgeItemFactory
from server.tests.factories.question_choice_factory import \
    QuestionChoiceFactory
from server.tests.factories.topic_factory import TopicFactory


@pytest.fixture
def subject_() -> Subject:
    return SubjectFactory(name="Chemistry")


@pytest.fixture
def knowledge_item_(topic_: Topic, subject_: Subject) -> KnowledgeItem:
    return KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id)


@pytest.fixture
def topic_(subject_) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def question_param(client: FlaskClient,
                   topic_: Topic,
                   knowledge_item_: KnowledgeItem) -> Dict:
    return build(dict,
                 knowledge_item=knowledge_item_,
                 topic=topic_,
                 FACTORY_CLASS=QuestionsFactory,
                 multiple_choice_question_type=True)


@pytest.fixture
def examboard() -> OrderedDict:
    return OrderedDict([('aqa', 'AQA')])


def test_question_creation_with_multiple_choices(client: FlaskClient,
                                                 topic_: Topic,
                                                 knowledge_item_: KnowledgeItem) -> None:
    question: Questions = QuestionsFactory.create(multiple_choice_question_type=True,
                                                  knowledge_item=knowledge_item_,
                                                  topic=topic_,
                                                  with_choices={
                                                      'choice_count': 4,
                                                      'choice_weight': 1,
                                                      'knowledge_item': knowledge_item_
                                                  })

    assert question.id is not None
    assert len(question.choices) == 4
    assert question.knowledge_item == knowledge_item_


def test_question_create_from_admin_form_succeeds(client: FlaskClient,
                                                  examboard: OrderedDict,
                                                  subject_: Subject) -> None:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             exam_board=examboard.get('aqa'),
                             subject=subject_.name,
                             multiple_choice_question_type=True)
    t = TopicFactory(subject_id=subject_.id)
    ki = KnowledgeItemFactory(topic_id=t.id, subject_id=subject_.id)

    question_payload.update({
        'choices': choices,
        'user_created': False,
        'topic': t.value,
        'knowledge_item': ki.value
    })
    q = Questions.create_from_admin_form(question_payload)

    assert q
    assert q.correct_choice
    assert q.exam_board


def test_question_create_from_admin_form_raises_error(client: FlaskClient) -> None:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             multiple_choice_question_type=True)

    question_payload['choices'] = choices
    question_payload['question'] = None

    with pytest.raises(ValidationError):
        Questions.create_from_admin_form(question_payload)


def test_question_correct_choice(client: FlaskClient,
                                 question_param: Dict,
                                 topic_: Topic,
                                 knowledge_item_: KnowledgeItem,
                                 subject_: Subject) -> None:
    q1 = QuestionsFactory.create(multiple_choice_question_type=True,
                                 knowledge_item=knowledge_item_,
                                 topic=topic_,
                                 with_choices={
                                     'choice_count': 4,
                                     'choice_weight': 1,
                                     'knowledge_item': knowledge_item_
                                 }, subject_id=subject_.id)
    q1.save()

    assert q1.correct_choice() is not None

    # choice = QuestionChoiceFactory.create()
    question_param['correct_choice_id'] = 1000

    q2 = Questions(**question_param)
    q2.save()

    assert q2.correct_choice() is None


def test_question_knowledge_item_relationship(client: FlaskClient,
                                              topic_: Topic,
                                              knowledge_item_: KnowledgeItem) -> None:
    question = QuestionsFactory.create(multiple_choice_question_type=True,
                                       knowledge_item=knowledge_item_,
                                       topic=topic_,
                                       with_choices={
                                           'choice_count': 4,
                                           'choice_weight': 1,
                                           'knowledge_item': knowledge_item_
                                       })

    assert question.knowledge_item == knowledge_item_
    assert question.knowledge_item_id is not None
    assert list(knowledge_item_.questions) == [question]


def test_question_topic_relationship(client: FlaskClient,
                                     topic_: Topic,
                                     knowledge_item_: KnowledgeItem) -> None:
    question = QuestionsFactory.create(multiple_choice_question_type=True,
                                       knowledge_item=knowledge_item_,
                                       topic=topic_,
                                       with_choices={
                                           'choice_count': 4,
                                           'choice_weight': 1,
                                           'knowledge_item': knowledge_item_
                                       })

    t = Topic.query.first()
    assert question.topic == t
    assert question.topic_id == t.id
    assert list(t.questions) == [question]
