import pytest
from server.models import QuestionTypeEnum


def test_questions_model(client, questions_factory):
    """
        Smoke test
    """
    question = questions_factory(multiple_choice_question_type=True)
    assert question.question_type == QuestionTypeEnum.multiple_choice


@pytest.mark.skip("Rethink mocking and model relationships")
def test_question_is_created_with_valid_correct_choice(client,
                                                       questions_factory,
                                                       question_choice_factory):
    pass
