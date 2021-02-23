import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Student
from server.tests.factories import StudentFactory


@pytest.fixture
def student_() -> Student:
    return StudentFactory(confirmed=False)


def test_student_account_confirmation(client: FlaskClient, student_: Student):
    token = student_.generate_confirmation_token()

    response = client.post(
        '/api/v1/student/confirm',
        json={
            "token": token
        }
    )

    assert response.status_code == 200
    assert student_.confirmed


def test_send_student_confirmation_success(client: FlaskClient,
                                           mocker: MockFixture,
                                           student_: Student) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions')

    response = client.get(f"api/v1/student/{student_.id}/send_confirmation")

    assert response.status_code == 200


def test_send_student_confirmation_student_not_found(client: FlaskClient,
                                                     mocker: MockFixture) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions')

    response = client.get("api/v1/student/100/send_confirmation")

    assert response.status_code == 404


def test_send_student_confirmation_exception(client: FlaskClient,
                                             student_: Student,
                                             mocker: MockFixture) -> None:

    def _mock_send_student_confirmation_instructions(*args, **kwargs):
        raise Exception()

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions',
                 _mock_send_student_confirmation_instructions)

    response = client.get(f"api/v1/student/{student_.id}/send_confirmation")

    assert response.status_code == 500
