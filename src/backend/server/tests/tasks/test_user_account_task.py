import pytest
from flask_mail import Message
from server.tasks import (send_account_recovery_instructions,
                          send_confirmation_instructions)
from server.tests.factories import TeacherFactory


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'rpc',
    }


@pytest.fixture
def teacher():
    return TeacherFactory.create()


def test_send_confirmation_instructions(client, teacher, mocker):
    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        send_confirmation_instructions(teacher.id)
        message = Message(subject="Hi! Your Quiz have arrived.")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html.assert_called_with(message,
                                               'account_confirmation.html.j2',
                                               confirmation_link=teacher.generate_confirmation_link())  # noqa


def test_send_account_recovery_instructions(client, teacher, mocker):

    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        send_account_recovery_instructions(teacher.email)

        message = Message(subject="Recover your account")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html.assert_called_with(message,
                                               'account_confirmation.html.j2',
                                               recovery_link=teacher.get_reset_link())

    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_error(send_mail_with_html):
        send_account_recovery_instructions("")

        send_mail_with_html.assert_not_called()
