from secrets import token_hex

import pytest
from faker import Faker
from faker.providers import internet
from flask.testing import FlaskClient
from flask_mail import Message
from pytest_mock import MockFixture
from server.models import Invitations, Teacher
from server.tasks import (send_account_recovery_instructions,
                          send_confirmation_instructions, send_user_invite)
from server.tests.factories import TeacherFactory


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'rpc',
    }


@pytest.fixture
def teacher() -> Teacher:
    return TeacherFactory.create()


fake = Faker()
fake.add_provider(internet)


@pytest.fixture
def invitations(teacher: Teacher) -> Invitations:
    invite = Invitations(fake.safe_email(), token_hex(8), teacher.id)
    invite.save()
    return invite


def test_send_confirmation_instructions(client: FlaskClient,
                                        teacher: Teacher,
                                        mocker: MockFixture):
    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        message = Message(subject="Confirm your account!")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html.assert_called_with(message,
                                               'account_confirmation.html.j2',
                                               confirmation_link=teacher.generate_confirmation_link())  # noqa
    send_confirmation_instructions(teacher.id)


def test_send_account_recovery_instructions(client: FlaskClient,
                                            teacher: Teacher,
                                            mocker: MockFixture):

    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):

        message = Message(subject="Recover your account")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html.assert_called_with(message,
                                               'account_recovery.html.j2',
                                               recovery_link=teacher.get_reset_link())
    send_account_recovery_instructions(teacher.email)


def test_send_account_recovery_instructions_error(client: FlaskClient,
                                                  teacher: Teacher,
                                                  mocker: MockFixture):
    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_error(send_mail_with_html):
        send_mail_with_html.assert_not_called()

    send_account_recovery_instructions("")


def test_send_user_invite(client: FlaskClient,
                          invitations: Invitations,
                          teacher: Teacher,
                          mocker: MockFixture):
    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        message = Message(subject="Your invite is here!")
        message.recipients = ["{}".format(invitations.email)]

        send_mail_with_html.assert_called_with(message,
                                               'user_invite.html.j2',
                                               inviter=str(teacher),
                                               invite_token=invitations.token)
    send_user_invite(invitations.email)
