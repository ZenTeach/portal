import pytest
from flask_mail import Message
from server.tasks import confirm_and_send_instruction
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


def test_confirm_and_send_instruction(client, teacher, mocker):
    # patch send_instruction

    @mocker.patch('server.tasks.user_account_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        confirm_and_send_instruction(teacher.id)
        message = Message(subject="Hi! Your Quiz have arrived.")
        message.recipients = ["{}".format(teacher.email)]

        send_mail_with_html.assert_called_with(message,
                                               'account_confirmation.html.j2',
                                               confirmation_link=teacher.generate_confirmation_link())  # noqa
