import re

from flask.testing import FlaskClient
from server.models import Teacher
from server.tests.factories import StudentFactory


def test_teacher_generate_confirmation_token(client: FlaskClient) -> None:
    teacher = Teacher.query.first()
    token = teacher.generate_confirmation_token()

    assert token is not None
    assert teacher.valid_confirmation_token(token)

    teacher.generate_confirmation_token()
    assert teacher.valid_confirmation_token(token)

    regex_link = re.compile(r'http:\/\/localhost:8080\/confirm_account\?token=([a-z0-9]*)')
    assert re.match(regex_link, teacher.generate_confirmation_link())

    teacher.confirm_user()
    assert teacher.confirmed_at is not None


def test_students_generate_confirmation_token(client: FlaskClient) -> None:
    student = StudentFactory.create(confirmed=False)
    token = student.generate_confirmation_token()

    assert token is not None
    assert student.valid_confirmation_token(token)

    student.generate_confirmation_token()
    assert student.valid_confirmation_token(token)

    regex_link = re.compile(r'http:\/\/localhost:8080\/confirm_account\?token=([a-z0-9]*)')
    assert re.match(regex_link, student.generate_confirmation_link())

    student.confirm_user()
    assert student.confirmed_at is not None
