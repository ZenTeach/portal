from server.tests.factories import TeacherFactory


def test_teacher_model(client):
    teacher = TeacherFactory.create()
    assert teacher


def test_teacher_confirmable(client):
    teacher = TeacherFactory.create()

    assert teacher.confirmed == False  # noqa
    assert teacher.confirmed_at is None
    assert teacher.confirmation_token is None
