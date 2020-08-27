import json

import pytest
from factory import build
from server.tests.factories import InvitationFactory, TeacherFactory


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
    assert response.status_code == status_code
    data = json.loads(response.data.decode())
    assert data == message


def test_teacher_registration_endpoint(client, teacher):
    new_teacher = build(dict, FACTORY_CLASS=TeacherFactory, with_invite_code=True)
    response = client.post(
        '/api/v1/teacher/registration',
        json=new_teacher
    )

    assert response.status_code == 400

    invite = InvitationFactory.create(invitation_from_id=teacher.id)
    valid_teacher_payload = build(dict,
                                  FACTORY_CLASS=TeacherFactory,
                                  email=invite.email,
                                  invitation_code=invite.token)

    success_response = client.post(
        '/api/v1/teacher/registration',
        json=valid_teacher_payload
    )

    assert success_response.status_code == 200


def test_teacher_account_confirmation(client, teacher):
    token = teacher.generate_confirmation_token()

    response = client.post(
        '/api/v1/teacher/confirm',
        json={
            "token": token
        }
    )

    assert response.status_code == 200
    assert teacher.confirmed


def test_teacher_account_recovery(client, teacher, mocker):
    token = teacher.get_reset_token()
    new_psswd = "FooPassword"

    @mocker.patch('server.api.teacher_auth_api.send_account_recovery_instructions.delay')
    def test_reset_get(send_account_recovery_instructions_delay):
        response = client.get(
            f'/api/v1/teacher/reset-password?email={teacher.email}'
        )

        send_account_recovery_instructions_delay.assert_called_with(teacher.email)
        assert response.status_code == 200

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


def test_teacher_user_invite(client, teacher, mocker, monkeypatch):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    invite_email = "invitee@someevent.com"

    @mocker.patch('server.api.teacher_auth_api.get_jwt_identity')
    def mock_identity():
        return {
            'email': teacher.email
        }

    @mocker.patch('server.api.teacher_auth_api.send_user_invite.delay')
    def test_success(send_user_invite_delay):
        response = client.post(
            '/api/v1/teacher/invite',
            json={
                'email': invite_email
            }
        )
        send_user_invite_delay.assert_called_with(invite_email)
        assert response.status_code == 200
