from server.tests.factories import TeacherFactory


def test_teacher_generate_confirmation_token(client):
    teacher = TeacherFactory.create()
    assert teacher.generate_confirmation_token() is not None
    assert teacher.generate_confirmation_token()


def test_teacher_confirm(client):
    teacher = TeacherFactory.create()
    teacher.confirm_user()

    assert teacher.confirmed_at is not None


def test_teacher_confirmation_token_validator(client):
    teacher = TeacherFactory.create()
    token = teacher.generate_confirmation_token()

    assert teacher.valid_token(token)

    teacher.generate_confirmation_token()
    assert teacher.valid_token(token)
