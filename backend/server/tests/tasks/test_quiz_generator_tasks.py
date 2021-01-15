import pytest
from flask.testing import FlaskClient
from flask_mail import Message
from pytest_mock import MockFixture
from server.models import ClassQuiz, Teacher
from server.tasks import send_quiz_generation_email
from server.tests.factories import (ClassQuizFactory, SchoolClassFactory,
                                    TeacherFactory)


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'rpc',
    }


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def classquiz_(teacher_: Teacher) -> ClassQuiz:
    sc = SchoolClassFactory.create(teacher_id=teacher_.id)
    cq = ClassQuizFactory.build(class_id=sc.id)
    cq.save()
    return cq


def test_send_quiz_generation_email(client: FlaskClient,
                                    mocker: MockFixture,
                                    teacher_: Teacher,
                                    classquiz_: ClassQuiz):
    @mocker.patch('server.tasks.quiz_generator_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        send_quiz_generation_email(teacher_.email, classquiz_.id)
        message = Message(subject="Hi! Your Quiz have arrived.")
        message.recipients = ["{}".format(teacher_.email)]
        send_mail_with_html.assert_called_with(
            message,
            "class_quiz_prepared.html.j2",
            full_name=teacher_.fullname(),
            quiz_link=classquiz_.url)
