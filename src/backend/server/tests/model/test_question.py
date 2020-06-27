from server.models import Questions, QuestionTypeEnum
from factory import build
import pytest
from server.tests.factories import QuestionsFactory, QuestionChoiceFactory
from uuid import uuid4

def test_questions_model(client, questions_factory):
    """
        Smoke test
    """
    question = questions_factory(multiple_choice_question_type=True)
    assert question.question_type == QuestionTypeEnum.multiple_choice


@pytest.mark.skip("Rethink mocking and model relationships")
def test_question_is_created_with_valid_correct_choice(client, questions_factory, question_choice_factory):
    question = QuestionsFactory.build(multiple_choice_question_type=True)
    choice_a = question_choice_factory(uuid=uuid4(), question=question.id)
    choice_b = question_choice_factory(uuid=uuid4(), question=question.id)
    choice_c = question_choice_factory(uuid=uuid4(), question=question.id, is_correct_choice=question)

    assert question.correct_choice_id == choice_c.id
