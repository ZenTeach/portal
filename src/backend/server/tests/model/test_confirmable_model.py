import re

from server.tests.factories import TeacherFactory


def test_teacher_generate_confirmation_token(client):
    teacher = TeacherFactory.create()
    token = teacher.generate_confirmation_token()

    assert token is not None
    assert teacher.valid_confirmation_token(token)

    teacher.generate_confirmation_token()
    assert teacher.valid_confirmation_token(token)

    regex_link = re.compile(r'http:\/\/localhost:8080\/confirm_account\?token=([a-z0-9]*)')
    assert re.match(regex_link, teacher.generate_confirmation_link())

    teacher.confirm_user()
    assert teacher.confirmed_at is not None
