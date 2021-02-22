import pytest
from flask.testing import FlaskClient
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
