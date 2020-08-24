import json

import pytest
from factory import build
from server.tests.factories import TeacherFactory


@pytest.fixture
def teacher():
    teacher = TeacherFactory(with_school_class=True,  # nosec
                             email="joemama@example.com", password="Asdfgh12!")
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
            "joemama@example.com", "Asdfgh12!", {
                'message': 'Logged in as joemama@example.com'}, 200
        )
    ],
)
def test_teacher_login_endpoint(client, teacher, email, password, message, status_code):
    response = client.post(
        '/api/v1/teacher/login',
        json={
            "email": email,
            "password": password
        }
    )
    assert response.status_code, status_code
    data = json.loads(response.data.decode())
    assert data == message


def test_teacher_registration_endpoint(client, teacher):
    new_teacher = build(dict, FACTORY_CLASS=TeacherFactory)
    response = client.post(
        '/api/v1/teacher/registration',
        json=new_teacher
    )

    assert response.status_code, 200


def test_teacher_account_confirmation(client, teacher):
    token = teacher.generate_confirmation_token()

    response = client.post(
        '/api/v1/teacher/confirm',
        json={
            "email": teacher.email,
            "token": token
        }
    )

    assert response.status_code == 200
    assert teacher.confirmed


def test_teacher_account_recovery(client, teacher):
    token = teacher.get_reset_token()
    new_psswd = "FooPassword"

    response = client.post(
        '/api/v1/teacher/reset-password',
        json={
            "email": teacher.email,
            "password": new_psswd,
            "token": token
        }
    )

    assert response.status_code == 200
    assert teacher.password != new_psswd

    relogin_response = client.post(
        '/api/v1/teacher/login',
        json={
            "email": teacher.email,
            "password": new_psswd
        }
    )

    assert relogin_response.status_code == 200
