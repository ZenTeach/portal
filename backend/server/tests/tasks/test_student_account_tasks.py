import pytest
from flask.testing import FlaskClient
from flask_mail import Message
from pytest_mock import MockFixture
from server.models import Student
from server.tasks import send_student_confirmation_instructions
from server.tests.factories import StudentFactory


@pytest.fixture
def student_() -> Student:
    return StudentFactory()


def test_send_student_confirmation_instructions(client: FlaskClient,
                                                student_: Student,
                                                mocker: MockFixture):
    def test_success(*args, **kwargs):
        message = Message(subject="Confirm your account!")
        message.recipients = ["{}".format(student_.email)]

        assert args[0].subject == message.subject
        assert args[0].recipients == message.recipients
        assert args[1] == "student_confirmation.html.j2"
        assert kwargs.get('confirmation_link') == student_.generate_confirmation_link(
            '/confirm_student_account')
        assert kwargs.get('full_name') == student_.full_name

    mocker.patch('server.tasks.student_account_tasks.send_mail_with_html', test_success)
    send_student_confirmation_instructions(student_.id)
