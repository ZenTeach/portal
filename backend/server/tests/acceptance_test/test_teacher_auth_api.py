import json

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Teacher
from server.tests.factories import InvitationFactory, TeacherFactory


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return TeacherFactory(with_school_class=True,  # nosec
                          email="joemama@example.com", password="Asdfgh12!")


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
def test_teacher_login_endpoint(client: FlaskClient,
                                teacher_: Teacher,
                                email: str,
                                password: str,
                                message: str,
                                status_code: int):
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


def test_teacher_registration_endpoint(client: FlaskClient,
                                       teacher_: Teacher,
                                       mocker: MockFixture):
    mocker.patch('server.api.teacher_auth_api.send_confirmation_instructions')
    new_teacher = build(dict, FACTORY_CLASS=TeacherFactory, with_invite_code=True)
    response = client.post(
        '/api/v1/teacher/registration',
        json=new_teacher
    )

    assert response.status_code == 400

    invite = InvitationFactory.create(invitation_from_id=teacher_.id)
    valid_teacher_payload = build(dict,
                                  FACTORY_CLASS=TeacherFactory,
                                  email=invite.email,
                                  invitation_code=invite.token)

    success_response = client.post(
        '/api/v1/teacher/registration',
        json=valid_teacher_payload
    )

    assert success_response.status_code == 200
    assert success_response.headers.get_all('Set-Cookie') is not None
    assert len(success_response.headers.get_all('Set-Cookie')) == 4


def test_teacher_account_confirmation(client: FlaskClient, teacher_: Teacher):
    token = teacher_.generate_confirmation_token()

    response = client.post(
        '/api/v1/teacher/confirm',
        json={
            "token": token
        }
    )

    assert response.status_code == 200
    assert teacher_.confirmed


def test_teacher_account_recovery(client: FlaskClient,
                                  teacher_: Teacher,
                                  mocker: MockFixture):
    token = teacher_.get_reset_token()
    new_psswd = "FooPassword"

    @mocker.patch('server.api.teacher_auth_api.send_account_recovery_instructions.delay')
    def test_reset_get(send_account_recovery_instructions_delay):
        response = client.get(
            f'/api/v1/teacher/reset-password?email={teacher_.email}'
        )

        send_account_recovery_instructions_delay.assert_called_with(teacher_.email)
        assert response.status_code == 200

    response = client.post(
        '/api/v1/teacher/reset-password',
        json={
            "email": teacher_.email,
            "password": new_psswd,
            "token": token
        }
    )

    assert response.status_code == 200
    assert teacher_.password != new_psswd

    relogin_response = client.post(
        '/api/v1/teacher/login',
        json={
            "email": teacher_.email,
            "password": new_psswd
        }
    )

    assert relogin_response.status_code == 200


def test_teacher_user_invite(client: FlaskClient,
                             teacher_: Teacher,
                             mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    invite_email = "invitee@someevent.com"

    @mocker.patch('server.api.teacher_auth_api.get_jwt_identity')
    def mock_identity():
        return {
            'email': teacher_.email
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


def test_teacher_token_refresh(client: FlaskClient,
                               teacher_: Teacher,
                               mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.teacher_auth_api.jwt_refresh_token_required')

    @mocker.patch('server.api.teacher_auth_api.get_jwt_identity')
    def mock_identity():
        return {
            'email': teacher_.email
        }

    @mocker.patch('server.api.teacher_auth_api.redis_store')
    def test_success(redis_store):
        response = client.post('/api/v1/teacher/token/refresh')

        redis_store.assert_called_once()
        assert response.status_code == 200


def test_teacher_logout(client: FlaskClient, teacher_: Teacher, mocker: MockFixture) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.teacher_auth_api.get_raw_jwt')
    mocker.patch('server.api.teacher_auth_api.redis_store')

    response = client.delete('/api/v1/teacher/logout')

    assert response.status_code == 204


def test_teacher_send_confirmartion(client: FlaskClient,
                                    teacher_: Teacher,
                                    mocker: MockFixture) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.teacher_auth_api.send_confirmation_instructions')
    # mocked_send_confirmation_instructions =

    response = client.post(
        '/api/v1/teacher/send_confirmation',
        json={
            'email': teacher_.email
        })

    assert response.status_code == 200
    # mocked_send_confirmation_instructions.assert_called()
    # mocked_send_confirmation_instructions.assert_called_with(teacher_.id)
