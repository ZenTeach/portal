import pytest
from server.models import QuestionTypeEnum
from server.tests.factories import QuestionsFactory


def test_questions_model(client):
    """
        Smoke test
    """
    question = QuestionsFactory.build(multiple_choice_question_type=True)
    assert question.question_type == QuestionTypeEnum.multiple_choice


@pytest.mark.skip("Rethink mocking and model relationships")
def test_question_is_created_with_valid_correct_choice(client):
    pass
