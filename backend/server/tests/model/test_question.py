from typing import Dict

import pytest
from factory import build
from flask.testing import FlaskClient
from marshmallow import ValidationError
from server.models import Questions
from server.tests.factories import QuestionsFactory
from server.tests.factories.question_choice_factory import \
    QuestionChoiceFactory


@pytest.fixture
def question_param(client: FlaskClient) -> Dict:
    return build(dict, FACTORY_CLASS=QuestionsFactory, multiple_choice_question_type=True)


def test_question_creation_with_multiple_choices(client: FlaskClient) -> None:
    question = QuestionsFactory.create(multiple_choice_question_type=True, with_choices=4)

    assert question.id is not None
    assert len(question.choices) == 4


def test_question_create_from_admin_form_succeeds(client: FlaskClient) -> None:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             multiple_choice_question_type=True)

    question_payload['choices'] = choices
    # import pdb; pdb.set_trace();
    q = Questions.create_from_admin_form(question_payload)

    assert q
    assert q.correct_choice


def test_question_create_from_admin_form_raises_error(client: FlaskClient) -> None:
    choices = [build(dict, FACTORY_CLASS=QuestionChoiceFactory,
                     weight=1, is_correct_choice=True) for _ in range(4)]
    question_payload = build(dict, FACTORY_CLASS=QuestionsFactory,
                             multiple_choice_question_type=True)

    question_payload['choices'] = choices
    del question_payload['question']

    with pytest.raises(ValidationError):
        Questions.create_from_admin_form(question_payload)


def test_question_correct_choice(client: FlaskClient, question_param: Dict) -> None:
    q1 = QuestionsFactory.create(multiple_choice_question_type=True, with_choices=4)
    q1.save()

    assert q1.correct_choice() is not None

    # choice = QuestionChoiceFactory.create()
    question_param['correct_choice_id'] = 1000

    q2 = Questions(**question_param)
    q2.save()

    assert q2.correct_choice() is None
