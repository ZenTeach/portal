from secrets import token_hex
from typing import List

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Student
from server.tests.factories import StudentFactory


@pytest.fixture
def student_(request) -> Student:
    return StudentFactory(confirmed=False)


@pytest.fixture
def anon_student_(client: FlaskClient, request) -> Student:
    st = Student.create_anonymous_student(password='Asdfgh12!', confirmed=True)  # nosec
    return st


@pytest.fixture
def unique_email() -> str:
    return token_hex(16) + "@example.com"


@pytest.fixture
def _access_token(client: FlaskClient, student_: Student) -> List[str]:
    import server
    from server.auth import (create_access_token, create_refresh_token,
                             get_csrf_token, get_jti)
    from server.auth.cookies import (ACCESS_COOKIE_NAME,
                                     ACCESS_CSRF_COOKIE_NAME,
                                     REFRESH_COOKIE_NAME,
                                     REFRESH_CSRF_COOKIE_NAME)

    access_token = create_access_token(
        student_.id, fresh=True, user_type="student"
    )
    refresh_token = create_refresh_token(student_.id, user_type="student")

    # Prime the client cookie jar with the same cookies the SPA would receive
    # from a real login, so FastAPI's cookie-based token resolution works.
    client.cookies.set(ACCESS_COOKIE_NAME, access_token)
    client.cookies.set(REFRESH_COOKIE_NAME, refresh_token)
    client.cookies.set(ACCESS_CSRF_COOKIE_NAME, get_csrf_token(access_token))
    client.cookies.set(REFRESH_CSRF_COOKIE_NAME, get_csrf_token(refresh_token))
    client.headers["X-CSRF-ACCESS-TOKEN"] = get_csrf_token(access_token)

    # Allowlist the jtis so the (allowlist-semantics) blocklist check passes.
    store = getattr(server, "redis_store", None)
    if store is not None:
        store.set(get_jti(access_token), "true")
        store.set(get_jti(refresh_token), "true")

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
    mocker.patch('server.routers.student_auth.send_student_confirmation_instructions')

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
    mocker.patch('server.routers.student_auth.send_student_confirmation_instructions')

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

    mocker.patch('server.routers.student_auth.send_student_confirmation_instructions',
                 _mock_send_student_confirmation_instructions)

    response = client.get(
        f"api/v1/student/{student_.id}/send_confirmation",
        headers={
            'Authorization': 'Bearer {}'.format(_access_token[0]),
            'X-CSRF-ACCESS-TOKEN': _access_token[2]
        })

    assert response.status_code == 500


def test_anon_student_auth(client: FlaskClient, anon_student_: Student):
    response = client.post(
        '/api/v1/student/login',
        json={
            "email": anon_student_.email,
            "password": "Asdfgh12!"
        })

    assert response.status_code == 200


# TODO: Waiting on https://github.com/vimalloc/flask-jwt-extended/issues/491
@pytest.mark.parametrize(
    "logged_in,new_email,current_student,status_code",
    [
        pytest.param(
            False, 'unique_email', 'anon_student_', 200
        ),
        pytest.param(
            False, 'unique_email', 'unique_email', 404
        )  # ,
        # pytest.param(
        #     False, 'unique_email', 'student_', 401
        # ),
        # pytest.param(
        #     True, 'unique_email', 'student_', 200
        # )
    ]
)
def test_student_current_endpoint(client: FlaskClient,
                                  logged_in: bool,
                                  new_email: str,
                                  current_student: str,
                                  _access_token: List[str],
                                  status_code: int,
                                  request):
    response = None
    current_email_or_student = request.getfixturevalue(current_student)
    new_email = request.getfixturevalue(new_email)
    current_email = current_email_or_student.email if isinstance(
        current_email_or_student, Student) else current_email_or_student
    if logged_in:
        response = client.put(
            '/api/v1/student/current',
            headers={
                'Authorization': 'Bearer {}'.format(_access_token[0]),
                'X-CSRF-ACCESS-TOKEN': _access_token[2]
            },
            json={
                "data": {
                    'email': new_email
                }
            }
        )
    else:
        response = client.put(
            '/api/v1/student/current',
            json={
                "email": current_email,
                "data": {
                    "email": new_email,
                }

            }
        )
    assert response.status_code == status_code
