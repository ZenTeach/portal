from json import loads
from uuid import uuid4

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import ClassQuiz, SchoolClass, Student, Teacher
from server.models.class_quiz import ClassQuizStatus
from server.models.quiz_session import QuizSession, QuizSessionStatus
from server.tests.factories import (ClassQuizFactory, SchoolClassFactory,
                                    StudentFactory, TeacherFactory)
from server.tests.factories.quiz_session_factory import QuizSessionFactory
from sqlalchemy import exc


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
def unconfirmed_student(school_class: SchoolClass) -> Student:
    student = StudentFactory(confirmed=False)
    school_class.add_student(student)
    return student


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


@pytest.fixture
def session_(student: Student, classquiz_: ClassQuiz) -> QuizSession:
    return QuizSessionFactory(student=student,
                              class_quiz=classquiz_,
                              status=QuizSessionStatus.created)


@pytest.fixture
def ended_session_(student: Student, classquiz_: ClassQuiz) -> QuizSession:
    return QuizSessionFactory(student=student,
                              class_quiz=classquiz_,
                              status=QuizSessionStatus.ended)


def test_get_quiz_submit(client: FlaskClient, student: Student, classquiz_: ClassQuiz):
    response = client.get(f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}")
    assert response.status_code == 200


def test_get_quiz_submit_not_confirmed_fails_with_400(client: FlaskClient,
                                                      unconfirmed_student: Student,
                                                      classquiz_: ClassQuiz) -> None:
    response = client.get(
        f"/api/v1/submit_quiz?email={unconfirmed_student.email}&quiz={classquiz_.uuid}")
    assert response.status_code == 400


def test_get_quiz_submit_without_student_email_fails_with_404(client: FlaskClient,
                                                              classquiz_: ClassQuiz):

    response = client.get(f"/api/v1/submit_quiz?email=cnajs@ajaksdcs.cs&quiz={classquiz_.uuid}")
    assert response.status_code == 404


def test_get_quiz_submit_without_class_quiz_fails_with_404(client: FlaskClient,
                                                           student: Student):

    response = client.get(f"/api/v1/submit_quiz?email={student.email}&quiz={uuid4()}")
    assert response.status_code == 404


def test_get_quiz_submit_with_existing_submission_fails_with_400(client: FlaskClient,
                                                                 student: Student,
                                                                 classquiz_: ClassQuiz,
                                                                 ended_session_: QuizSession):

    response = client.get(f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}")
    assert response.status_code == 400


def test_get_quiz_submit_with_database_error_fails_with_500(client: FlaskClient,
                                                            student: Student,
                                                            classquiz_: ClassQuiz,
                                                            mocker: MockFixture):

    def _mock_add_student_session(*args):
        raise exc.DatabaseError('', '', '')

    mocker.patch.object(ClassQuiz, 'add_student_session', _mock_add_student_session)
    response = client.get(f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}")
    assert response.status_code == 500


def test_get_endpoint_idempotency(client: FlaskClient,
                                  student: Student,
                                  classquiz_: ClassQuiz,
                                  session_: QuizSession,
                                  mocker: MockFixture):

    response = client.get(f"/api/v1/submit_quiz?email={student.email}&quiz={classquiz_.uuid}")
    assert response.status_code == 200
    assert QuizSession.query.count() == 1


def test_post_quiz_submit(client: FlaskClient,
                          student: Student,
                          classquiz_: ClassQuiz,
                          session_: QuizSession,
                          mocker: MockFixture):

    @mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    def _mock_grader_administered_quizzes(*args):
        assert len(args) == 1
        assert args[0] == classquiz_.uuid

    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })

    assert response.status_code == 201
    assert classquiz_.status == ClassQuizStatus.administered
    assert session_.status == QuizSessionStatus.ended


def test_post_student_not_found_error(client: FlaskClient,
                                      classquiz_: ClassQuiz,
                                      session_: QuizSession,
                                      mocker: MockFixture):

    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": "dummy@example.com",
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })

    assert response.status_code == 404
    assert session_.status == QuizSessionStatus.created

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Student with email dummy@example.com doesn't exist"


def test_post_classquiz_not_found_error(client: FlaskClient,
                                        student: Student,
                                        session_: QuizSession,
                                        mocker: MockFixture):
    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": uuid4(),
                               "data": []
                           })

    assert response.status_code == 404
    assert session_.status == QuizSessionStatus.created

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Class Quiz doesn't exist"


def test_post_quizsession_not_found_error(client: FlaskClient,
                                          student: Student,
                                          classquiz_: ClassQuiz,
                                          mocker: MockFixture):
    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })

    assert response.status_code == 404

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Quiz not started"


def test_post_quizsession_ended_error(client: FlaskClient,
                                      student: Student,
                                      classquiz_: ClassQuiz,
                                      ended_session_: QuizSession,
                                      mocker: MockFixture):

    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })

    assert response.status_code == 404

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Session has ended!"


def test_post_db_exception(client: FlaskClient,
                           student: Student,
                           classquiz_: ClassQuiz,
                           session_: QuizSession,
                           mocker: MockFixture):

    def _mock_student_save(*args):
        raise exc.IntegrityError('', '', '')

    mocker.patch.object(Student, 'save', _mock_student_save)
    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })

    assert response.status_code == 500

    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Encountered a server error"


def test_post_endpoint_idempotency(client: FlaskClient,
                                   student: Student,
                                   classquiz_: ClassQuiz,
                                   ended_session_: QuizSession,
                                   mocker: MockFixture):

    mocker.patch('server.api.quiz_submit_api.grader_administered_quizzes')
    response = client.post("/api/v1/submit_quiz",
                           json={
                               "StudentEmail": student.email,
                               "QuizId": classquiz_.uuid,
                               "data": []
                           })
    assert response.status_code == 404
