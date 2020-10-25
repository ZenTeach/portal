import os

import pytest
from faker import Faker
from faker.providers import internet
from flask_mail import Message
from server.tasks.commons import send_mail, send_mail_with_html

fake = Faker()
fake.add_provider(internet)


@pytest.fixture
def message():
    return Message(subject="Dummy subject")


@pytest.fixture
def mock_email_address():
    return fake.safe_email()


def test_send_mail(client, mocker, mock_email_address, message):
    mocker.patch.dict(os.environ, {"DEFAULT_MAIL_SENDER": mock_email_address})
    mocker.patch('server.tasks.commons.mail')

    @mocker.patch('server.tasks.commons.attach_sender')
    def test_success(attach_sender):
        send_mail(message)

        attach_sender.assert_called_with(message)
        assert message.sender == mock_email_address


def test_send_mail_with_html(client, mocker, mock_email_address, message):
    mocker.patch.dict(os.environ, {"DEFAULT_MAIL_SENDER": mock_email_address})
    mocker.patch('server.tasks.commons.mail')
    mocker.patch('flask.render_template')

    @mocker.patch('server.tasks.commons.attach_sender')
    def test_success(attach_sender):
        send_mail_with_html(message, 'dummy template')

        attach_sender.assert_called_with(message)
        assert message.sender == mock_email_address
