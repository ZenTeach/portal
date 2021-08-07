from typing import Dict, OrderedDict

import pytest
from factory import build
from flask.testing import FlaskClient
from marshmallow import ValidationError
from server.models import KnowledgeItem, Questions, Subject
from server.tests.factories import QuestionsFactory
from server.tests.factories.knowledge_item_factory import KnowledgeItemFactory
from server.tests.factories.question_choice_factory import \
    QuestionChoiceFactory


@pytest.fixture
def subject_() -> Subject:
    s = Subject(name="Chemistry", enabled=True)
    s.save()
    return s


@pytest.fixture
def knowledge_item_() -> KnowledgeItem:
    return KnowledgeItemFactory()


@pytest.fixture
def question_param(client: FlaskClient) -> Dict:
    return build(dict, FACTORY_CLASS=QuestionsFactory, multiple_choice_question_type=True)


@pytest.fixture
def examboard() -> OrderedDict:
    return OrderedDict([('aqa', 'AQA')])


def test_question_creation_with_multiple_choices(client: FlaskClient,
                                                 knowledge_item_: KnowledgeItem) -> None:
    question = QuestionsFactory.create(multiple_choice_question_type=True,
                                       with_choices={
                                           'choice_count': 4,
                                           'choice_weight': 1,
                                           'knowledge_item': knowledge_item_
                                       })

    assert question.id is not None
    assert len(question.choices) == 4


def test_question_create_from_admin_form_succeeds(client: FlaskClient,
                                                  examboard: OrderedDict,
                                                  subject_: Subject) -> None:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             exam_board=examboard.get('aqa'),
                             subject=subject_.name,
                             multiple_choice_question_type=True)

    question_payload.update({'choices': choices, 'user_created': False})
    q = Questions.create_from_admin_form(question_payload)

    assert q
    assert q.correct_choice


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
                                 knowledge_item_: KnowledgeItem,
                                 subject_: Subject) -> None:
    q1 = QuestionsFactory.create(multiple_choice_question_type=True,
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
                                              knowledge_item_: KnowledgeItem) -> None:
    question = QuestionsFactory.create(multiple_choice_question_type=True,
                                       with_choices={
                                           'choice_count': 4,
                                           'choice_weight': 1,
                                           'knowledge_item': knowledge_item_
                                       })

    assert question._knowledge_item == knowledge_item_
    assert question._knowledge_item_id is not None
    assert knowledge_item_.questions == [question]
