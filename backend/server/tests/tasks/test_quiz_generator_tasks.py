import pytest
from flask_mail import Message
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
def teacher():
    return TeacherFactory.create()


@pytest.fixture
def classquiz_(teacher):
    sc = SchoolClassFactory.create(teacher_id=teacher.id)
    cq = ClassQuizFactory.build(class_id=sc.id)
    cq.save()
    return cq


def test_send_quiz_generation_email(client, mocker, teacher, classquiz_):
    @mocker.patch('server.tasks.quiz_generator_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        send_quiz_generation_email(teacher.email, classquiz_.id)
        message = Message(subject="Hi! Your Quiz have arrived.")
        message.recipients = ["{}".format(teacher.email)]
        send_mail_with_html.assert_called_with(
            message,
            "class_quiz_prepared.html.j2",
            full_name=teacher.fullname(),
            quiz_link=classquiz_.url)
