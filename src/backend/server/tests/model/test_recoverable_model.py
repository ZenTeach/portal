import re

from server.tests.factories import TeacherFactory


def test_reset_functions(client):
    teacher = TeacherFactory.create()

    assert teacher.recovery_token is None
    assert teacher.recovered_at is None

    token = teacher.get_reset_token()

    assert token == teacher.recovery_token
    assert teacher.recovered_at is None

    assert teacher.valid_recovery_token(token)

    token_link = teacher.get_reset_link()
    regex_link = re.compile(
        r'http:\/\/localhost:8080\/change_password\?token=([a-z0-9]*)&email=([a-z0-9]*)')
    assert re.match(regex_link, token_link)


def test_reset_account(client):
    teacher = TeacherFactory.create()

    token = teacher.get_reset_token()
    new_psswd = "FooPassword"
    teacher.reset_account(token, new_psswd)

    assert teacher.password == new_psswd
    assert teacher.recovered_at is not None
    assert teacher.recovery_token is None
