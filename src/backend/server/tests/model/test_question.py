from server.models import Questions, QuestionTypeEnum
from uuid import uuid4
def test_questions_model(client, questions_factory):
    """
        Smoke test
    """
    question = questions_factory(multiple_choice_question_type=True)
    assert question.question_type == QuestionTypeEnum.multiple_choice



def test_question_is_created_with_valid_correct_choice(client, questions_factory, question_choice_factory):
    question = questions_factory(uuid=uuid4(), multiple_choice_question_type=True)
    choice_a = question_choice_factory(uuid=uuid4(), question=question.id)
    choice_b = question_choice_factory(uuid=uuid4(), question=question.id)
    choice_c = question_choice_factory(uuid=uuid4(), question=question.id, is_correct_choice=question)

    assert question.correct_choice == choice_c
