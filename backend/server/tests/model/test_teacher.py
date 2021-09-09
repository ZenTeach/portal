import pytest
from server.models import Questions, Teacher
from server.tests.factories import QuestionsFactory, TeacherFactory


@pytest.fixture
def questions_() -> Questions:
    return QuestionsFactory(multiple_choice_question_type=True, with_choices=4)


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


def test_teacher_model(client):
    teacher = TeacherFactory.create()
    assert teacher


def test_teacher_confirmable(client):
    teacher = TeacherFactory.create()

    assert teacher.confirmed == False  # noqa
    assert teacher.confirmed_at is None
    assert teacher.confirmation_token is None


def test_teacher_add_question(client, teacher_, questions_):
    teacher_.questions.append(questions_)

    assert teacher_.questions[0] == questions_
    assert questions_.teacher_id == teacher_.id


def test_teacher_remove_question(client, teacher_, questions_):
    questions_.teacher_id = teacher_.id
    questions_.save()
    teacher_.reload()

    teacher_.questions.pop()
    questions_.reload()

    assert teacher_.questions == []
    assert questions_.teacher_id is None
