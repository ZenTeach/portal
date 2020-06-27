import json
import pytest
from server.tests.factories import TeacherFactory
from factory import build

@pytest.fixture
def teacher():
    teacher = TeacherFactory(with_school_class=True, email="joemama@example.com", password="Asdfgh12!")
    return teacher

@pytest.mark.parametrize(
    "email,password,message,status_code",
    [
        pytest.param(
            "", "", {'message': 'User  doesn\'t exist'}, 404
        ),
        pytest.param(
            "joemama@example.com", "123456789", {'message': 'Wrong credentials'}, 400
        ),
        pytest.param(
            "joe@example.com", "123456789", {'message': 'User joe@example.com doesn\'t exist'}, 404
        ),
        pytest.param(
            "joemama@example.com", "Asdfgh12!", {'message': 'Logged in as joemama@example.com'}, 200
        )
    ],
)
def test_teacher_login_endpoint(client, teacher, email, password, message, status_code):
    response = client.post(
        '/api/v1/teacher/login',
        json = {
            "email": email,
            "password": password
        }
    )
    assert response.status_code, status_code
    # assert len(response.headers.get_all('Set-Cookie')), 4
    data = json.loads(response.data.decode())
    assert data == message


def test_teacher_registration_endpoint(client, teacher):
    new_teacher = build(dict, FACTORY_CLASS=TeacherFactory)
    response = client.post(
        '/api/v1/teacher/registration',
        json = new_teacher
    )

    assert response.status_code, 200
