from json import loads
from typing import List
from uuid import uuid4

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import ClassQuiz, SchoolClass, Student, Teacher
from server.models.quiz_session import QuizSession, QuizSessionStatus
from server.tests.factories import (ClassQuizFactory, SchoolClassFactory,
                                    StudentFactory)
from server.tests.factories.quiz_session_factory import QuizSessionFactory
from sqlalchemy import exc


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
def unconfirmed_student(school_class: SchoolClass) -> Student:
    student = StudentFactory(confirmed=False)
    school_class.add_student(student)
    return student


@pytest.fixture
def classquiz_(school_class: SchoolClass,) -> ClassQuiz:

    cq = ClassQuizFactory.create(class_id=school_class.id,
                                 with_multiple_choice_questions=4)
    return cq


@pytest.fixture
def public_classquiz_(school_class: SchoolClass,) -> ClassQuiz:

    cq = ClassQuizFactory.create(class_id=school_class.id,
                                 private=False,
                                 with_multiple_choice_questions=4)
    return cq


@pytest.fixture
def student_response(classquiz_: ClassQuiz) -> List[dict]:
    return [
        {
            "questionID": question['id'],
            "Choice_answer": question['choices'][0]['uuid']
        }
        for question in classquiz_.questions
    ]


@pytest.fixture
def session_(student: Student, classquiz_: ClassQuiz) -> QuizSession:
    qsession = QuizSessionFactory(student=student,
                                  class_quiz=classquiz_,
                                  status=QuizSessionStatus.created)
    qsession.save()
    return qsession


@pytest.fixture
def ended_session_(student: Student, classquiz_: ClassQuiz) -> QuizSession:
    qsession = QuizSessionFactory(student=student,
                                  class_quiz=classquiz_,
                                  status=QuizSessionStatus.ended)
    qsession.save()
    return qsession


def test_get_quiz_submit(client: FlaskClient,
                         student: Student,
                         classquiz_: ClassQuiz,
                         access_token: List[str]):
    student_email = student.email.capitalize()
    response = client.get(
        f"/api/v1/submit_quiz?email={student_email}&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200


def test_get_quiz_submit_not_confirmed_fails_with_400(client: FlaskClient,
                                                      unconfirmed_student: Student,
                                                      access_token: List[str],
                                                      classquiz_: ClassQuiz) -> None:
    response = client.get(
        f"/api/v1/submit_quiz?email={unconfirmed_student.email}&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 400


def test_get_quiz_submit_without_valid_student_email_fails_with_404(client: FlaskClient,
                                                                    access_token: List[str],
                                                                    classquiz_: ClassQuiz):

    response = client.get(
        f"/api/v1/submit_quiz?email=cnajs@ajaksdcs.cs&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 404


def test_get_quiz_submit_without_class_quiz_fails_with_404(client: FlaskClient,
                                                           access_token: List[str],
                                                           student: Student):

    response = client.get(
        f"/api/v1/submit_quiz?email={student.email}&quiz={uuid4()}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 404


def test_get_quiz_submit_with_existing_submission_fails_with_400(client: FlaskClient,
                                                                 student: Student,
                                                                 classquiz_: ClassQuiz,
                                                                 access_token: List[str],
                                                                 ended_session_: QuizSession):

    response = client.get(
        f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 400


def test_get_quiz_submit_with_database_error_fails_with_500(client: FlaskClient,
                                                            student: Student,
                                                            classquiz_: ClassQuiz,
                                                            access_token: List[str],
                                                            mocker: MockFixture):

    def _mock_add_student_session(*args):
        raise exc.DatabaseError('', '', '')

    mocker.patch.object(ClassQuiz, 'add_student_session', _mock_add_student_session)
    response = client.get(
        f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 500


def test_get_endpoint_idempotency(client: FlaskClient,
                                  student: Student,
                                  classquiz_: ClassQuiz,
                                  access_token: List[str]):

    response = client.get(
        f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200
    assert QuizSession.query.count() == 1


def test_get_quiz_submit_with_anonymous_user(client: FlaskClient,
                                             public_classquiz_: ClassQuiz,
                                             access_token: List[str]):

    response = client.get(
        f"/api/v1/submit_quiz?quiz={public_classquiz_.uuid}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200
    assert QuizSession.query.count() == 1
    student = Student.query.first()
    data = response.get_json()["data"]
    assert data['anonymous_student_email'] == student.email
    assert data['anonymous_student_password'] == 'Asdfgh12!'


def test_post_quiz_submit(client: FlaskClient,
                          student: Student,
                          classquiz_: ClassQuiz,
                          access_token: List[str],
                          session_: QuizSession,
                          student_response: List[dict]):

    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": classquiz_.uuid,
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 201
    assert session_.status == QuizSessionStatus.ended


def test_post_student_not_found_error(client: FlaskClient,
                                      classquiz_: ClassQuiz,
                                      session_: QuizSession,
                                      access_token: List[str],
                                      student_response: List[dict]):

    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": "dummy@example.com",
            "QuizId": classquiz_.uuid,
            "data": student_response
        }, headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404
    assert session_.status == QuizSessionStatus.created

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Student with email dummy@example.com doesn't exist"


def test_post_classquiz_not_found_error(client: FlaskClient,
                                        student: Student,
                                        student_response: List[dict],
                                        access_token: List[str],
                                        session_: QuizSession):
    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": uuid4(),
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404
    assert session_.status == QuizSessionStatus.created

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Class Quiz doesn't exist"


def test_post_quizsession_not_found_error(client: FlaskClient,
                                          student: Student,
                                          student_response: List[dict],
                                          access_token: List[str],
                                          classquiz_: ClassQuiz):
    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": classquiz_.uuid,
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Quiz not started"


def test_post_quizsession_ended_error(client: FlaskClient,
                                      student: Student,
                                      classquiz_: ClassQuiz,
                                      student_response: List[dict],
                                      ended_session_: QuizSession,
                                      access_token: List[str],
                                      mocker: MockFixture):
    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": classquiz_.uuid,
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Session has ended!"


def test_post_db_exception(client: FlaskClient,
                           student: Student,
                           classquiz_: ClassQuiz,
                           student_response: List[dict],
                           access_token: List[str],
                           session_: QuizSession,
                           mocker: MockFixture):
    def _mock_student_save(*args):
        raise exc.IntegrityError('', '', '')

    mocker.patch.object(Student, 'save', _mock_student_save)
    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": classquiz_.uuid,
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 500

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Encountered a server error"


def test_post_endpoint_idempotency(client: FlaskClient,
                                   student: Student,
                                   classquiz_: ClassQuiz,
                                   access_token: List[str],
                                   student_response: List[dict]):

    response = client.post(
        "/api/v1/submit_quiz",
        json={
            "StudentEmail": student.email,
            "QuizId": classquiz_.uuid,
            "data": student_response
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 404
