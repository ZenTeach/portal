from uuid import uuid4

import pytest
from flask.testing import FlaskClient
from flask_mail import Message
from pytest_mock import MockFixture
from server.models import ClassQuiz, QuizGrade, SchoolClass, Student, Teacher
from server.tasks import send_graded_quizzes, send_report_card_pdf
from server.tests.factories import (ClassQuizFactory, QuizGradeFactory,
                                    SchoolClassFactory, StudentFactory)


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'rpc',
    }


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def anon_student(school_class: SchoolClass) -> Student:
    return Student.create_anonymous_student(classes=[school_class])


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


@pytest.fixture
def quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id,
                            graded=True,
                            result_sent=False,
                            score=0)


@pytest.fixture
def anon_student_quiz_grade(anon_student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=anon_student.id,
                            uuid=uuid4(),
                            class_quiz_id=classquiz_.id,
                            graded=True,
                            result_sent=False,
                            score=0)


@pytest.fixture
def unsent_quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id,
                            graded=True,
                            result_sent=False,
                            score=0)


def test_send_report_card_pdf(client: FlaskClient,
                              mocker: MockFixture,
                              anon_student_quiz_grade: QuizGrade,
                              quiz_grade: QuizGrade) -> None:

    @mocker.patch('server.tasks.quiz_generator_tasks.send_mail_with_html')
    def test_success(update_and_save, send_mail_with_html):
        message = Message(subject="Hi! Your Report Card PDF has arrived")
        message.recipients = ["{}".format(quiz_grade.student.email)]

        send_mail_with_html.assert_called_with(
            message,
            "report_card.html.j2",
            full_name=quiz_grade.student.full_name)
        assert send_mail_with_html.call_count == 1

    send_report_card_pdf(quiz_grade.uuid)
    report_card_not_generated = send_report_card_pdf(anon_student_quiz_grade.uuid)
    assert quiz_grade.result_sent
    assert not anon_student_quiz_grade.result_sent
    assert report_card_not_generated is None


def test_graded_quizzes(client: FlaskClient,
                        mocker: MockFixture,
                        unsent_quiz_grade: QuizGrade) -> None:
    mocked_send_report_card = mocker.patch(
        'server.tasks.report_card_task.send_report_card_pdf.apply_async')
    send_graded_quizzes()
    mocked_send_report_card.assert_called_once()
