from typing import List

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Student
from server.tests.factories import StudentFactory


@pytest.fixture
def student_() -> Student:
    return StudentFactory(confirmed=False)


@pytest.fixture(autouse=True)
def _access_token(client: FlaskClient, student_: Student) -> List[str]:
    from datetime import timedelta

    from flask_jwt_extended import (create_access_token, create_refresh_token,
                                    get_csrf_token, get_jti)
    from server import redis_store
    from server.lib.utils.jwt_fixes import (set_access_cookies,
                                            set_refresh_cookies)

    access_token = create_access_token(student_.id, fresh=True)
    refresh_token = create_refresh_token(student_.id)
    set_access_cookies(client, access_token, legacy=True)
    set_refresh_cookies(client, refresh_token, legacy=True)
    access_jti = get_jti(access_token)
    refresh_jti = get_jti(refresh_token)
    redis_store.set(access_jti, "true", timedelta(minutes=30) * 1.2)
    redis_store.set(refresh_jti, "true", timedelta(minutes=30) * 1.2)

    return [access_token,
            refresh_token,
            get_csrf_token(access_token),
            get_csrf_token(refresh_token)]


@pytest.mark.xfail(reason="Broken fixture factory")
def test_student_registration_endpoint(client: FlaskClient,
                                       mocker: MockFixture):
    import random
    random.seed(1000)
    new_student = build(dict, FACTORY_CLASS=StudentFactory)
    response = client.post(
        '/api/v1/student/registration',
        json=new_student
    )

    assert response.status_code == 200
    assert response.headers.get('Set-Cookie') is not None


def test_student_account_confirmation(client: FlaskClient,
                                      _access_token: List[str],
                                      student_: Student):
    token = student_.generate_confirmation_token()

    response = client.post(
        '/api/v1/student/confirm',
        json={
            "token": token
        },
        headers={
            'Authorization': 'Bearer {}'.format(_access_token[0]),
            'X-CSRF-ACCESS-TOKEN': _access_token[2]
        }
    )

    assert response.status_code == 200
    assert student_.confirmed


def test_send_student_confirmation_success(client: FlaskClient,
                                           mocker: MockFixture,
                                           _access_token: List[str],
                                           student_: Student) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions')

    response = client.get(
        f"api/v1/student/{student_.id}/send_confirmation",
        headers={
            'Authorization': 'Bearer {}'.format(_access_token[0]),
            'X-CSRF-ACCESS-TOKEN': _access_token[2]
        })

    assert response.status_code == 200


def test_send_student_confirmation_student_not_found(client: FlaskClient,
                                                     _access_token: List[str],
                                                     mocker: MockFixture) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions')

    response = client.get(
        "api/v1/student/100/send_confirmation",
        headers={
            'Authorization': 'Bearer {}'.format(_access_token[0]),
            'X-CSRF-ACCESS-TOKEN': _access_token[2]
        })

    assert response.status_code == 404


def test_send_student_confirmation_exception(client: FlaskClient,
                                             student_: Student,
                                             _access_token: List[str],
                                             mocker: MockFixture) -> None:

    def _mock_send_student_confirmation_instructions(*args, **kwargs):
        raise Exception()

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.student_auth_api.send_student_confirmation_instructions',
                 _mock_send_student_confirmation_instructions)

    response = client.get(
        f"api/v1/student/{student_.id}/send_confirmation",
        headers={
            'Authorization': 'Bearer {}'.format(_access_token[0]),
            'X-CSRF-ACCESS-TOKEN': _access_token[2]
        })

    assert response.status_code == 500
