import pytest
from flask.testing import FlaskClient
from flask_mail import Message
from pytest_mock import MockFixture
from server.models import ClassQuiz, QuizGrade, SchoolClass, Student, Teacher
from server.tasks import send_report_card_pdf
from server.tests.factories import (ClassQuizFactory, QuizGradeFactory,
                                    SchoolClassFactory, StudentFactory,
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
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


@pytest.fixture
def quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, graded=True, score=None)


def test_send_report_card_pdf(client: FlaskClient,
                              mocker: MockFixture,
                              quiz_grade: QuizGrade) -> None:

    @mocker.patch('server.tasks.quiz_generator_tasks.send_mail_with_html')
    def test_success(send_mail_with_html):
        send_report_card_pdf(quiz_grade.uuid)
        message = Message(subject="Hi! Your Report Card PDF has arrived")
        message.recipients = ["{}".format(quiz_grade.student.email)]

        send_mail_with_html.assert_called_with(
            message,
            "report_card.html.j2",
            full_name=quiz_grade.student.full_name)
