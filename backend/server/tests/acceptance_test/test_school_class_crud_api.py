import json
from json import loads
from random import choice
from typing import Dict, List

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import SchoolClass, Subject, Teacher
from server.models.student import Student
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)
from sqlalchemy import exc


@pytest.fixture(autouse=True)
def subjects_(client: FlaskClient) -> None:
    for subject in ['Biology', 'Chemistry', 'Physics']:
        Subject(name=subject, enabled=True).save()


@pytest.fixture()
def subject_() -> Subject:
    return Subject.query.first()


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def student() -> Student:
    return StudentFactory.create()


@pytest.fixture
def school_class(teacher_: Teacher, subject_: Subject) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id, subject_id=subject_.id)


@pytest.fixture
def school_class_param(teacher_: Teacher) -> dict:
    return build(dict,
                 FACTORY_CLASS=SchoolClassFactory,
                 subject=choice(['Chemistry', 'Biology', 'Physics']),
                 teacher_id=teacher_.id)


@pytest.fixture
def update_school_class_param(teacher_: Teacher) -> dict:
    return build(dict,
                 FACTORY_CLASS=SchoolClassFactory,
                 teacher_id=teacher_.id)


@pytest.fixture
def mock_identity(teacher_: Teacher) -> dict:
    return {
        'identity': {
            'id': teacher_.id,
            'email': teacher_.email
        }
    }


def test_get_school_class_with_id(client: FlaskClient,
                                  student: Student,
                                  school_class: SchoolClass,
                                  access_token: List[str],
                                  mocker: MockFixture):
    school_class.add_student(student)
    response = client.get(
        "/api/v1/school_class/{}".format(school_class.id),
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200

    data = json.loads(response.data.decode())["data"]

    assert data["id"] == school_class.id
    assert data["students"][0]["id"] == student.id


def test_create_school_class(client: FlaskClient,
                             mocker: MockFixture,
                             mock_identity: dict,
                             access_token: List[str],
                             teacher_identity: Teacher,
                             school_class_param: dict):
    response = client.post(
        "/api/v1/school_class",
        json=school_class_param,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data == {
        "status": "success",
        "message": "{} was added!".format(school_class_param["name"]),
    }


def test_fetch_school_class_list(client: FlaskClient,
                                 access_token: List[str],
                                 mocker: MockFixture):
    SchoolClassFactory.create_batch(5)

    response = client.get(
        "/api/v1/school_class",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data["data"]["school_classes"]) == 5


def test_delete_school_class(client: FlaskClient,
                             mocker: MockFixture,
                             access_token: List[str],
                             school_class: SchoolClass):
    response = client.delete(
        f'/api/v1/school_class/{school_class.id}',
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 204


def test_post_add_student_to_school_class(client: FlaskClient,
                                          mocker: MockFixture,
                                          access_token: List[str],
                                          school_class: SchoolClass):
    mocker.patch('server.api.school_class_api.send_student_confirmation_instructions')

    student_payload = {
        'firstname': 'Michael',
        'lastname': 'Scott',
        'email': 'mscott@dunder-mifflin.com'
    }

    response = client.post(
        f'/api/v1/school_class/{school_class.id}/student',
        json=student_payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert len(school_class.students) == 1
    assert response.status_code == 201


def test_post_add_existing_student_to_school_class(client: FlaskClient,
                                                   mocker: MockFixture,
                                                   school_class: SchoolClass,
                                                   access_token: List[str],
                                                   student: Student):
    mocker.patch('server.api.school_class_api.send_student_confirmation_instructions')
    school_class.add_student(student)

    student_payload = {
        'firstname': student.firstname,
        'lastname': student.lastname,
        'email': student.email
    }

    response = client.post(
        f'/api/v1/school_class/{school_class.id}/student',
        json=student_payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert len(school_class.students) == 1
    assert response.status_code == 201


def test_delete_remove_student_from_school_class(client: FlaskClient,
                                                 mocker: MockFixture,
                                                 school_class: SchoolClass,
                                                 access_token: List[str],
                                                 student: Student):
    school_class.add_student(student)

    assert len(school_class.students) != 0

    response = client.delete(
        f'/api/v1/school_class/{school_class.id}/student?student_id={student.id}',
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 204
    assert len(school_class.students) == 0


def test_patch_update_student_email_in_school_class(client: FlaskClient,
                                                    mocker: MockFixture,
                                                    school_class: SchoolClass,
                                                    access_token: List[str],
                                                    student: Student):
    mocker.patch('server.api.school_class_api.send_student_confirmation_instructions')
    school_class.add_student(student)

    assert student.confirmed
    response = client.patch(
        f'/api/v1/school_class/{school_class.id}/student',
        json={
            'old_email': student.email,
            'new_email': 'test@example.com'
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200
    student.reload()
    assert not student.confirmed
    assert student.email == "test@example.com"


def test_patch_update_student_email_if_school_class_not_found(client: FlaskClient,
                                                              mocker: MockFixture,
                                                              school_class: SchoolClass,
                                                              access_token: List[str],
                                                              student: Student):
    school_class.add_student(student)

    response = client.patch(
        '/api/v1/school_class/10/student',
        json={
            'old_email': student.email,
            'new_email': 'test@example.com'
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404
    data = loads(response.data.decode("utf-8"))['message']
    assert data == "School class room doesn't exist"


def test_patch_update_student_email_if_student_not_found(client: FlaskClient,
                                                         mocker: MockFixture,
                                                         school_class: SchoolClass,
                                                         access_token: List[str],
                                                         student: Student):
    school_class.add_student(student)

    response = client.patch(
        f'/api/v1/school_class/{school_class.id}/student',
        json={
            'old_email': 'nksl@cnajskajs.cs',
            'new_email': 'test@example.com'
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 404
    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Student not found!"


@pytest.mark.parametrize('payload', [
    pytest.param({
        'old_email': 'acmaosdaos',
        'new_email': 'test@example.com'
    }),
    pytest.param({
        'old_email': 'acmaosdaos',
        'new_email': 'test.com'
    }),
    pytest.param({
        'old_email': 'acmaosdaos',
    }),
    pytest.param({})
])
def test_patch_update_student_email_malformed_data_error(client: FlaskClient,
                                                         mocker: MockFixture,
                                                         school_class: SchoolClass,
                                                         student: Student,
                                                         access_token: List[str],
                                                         payload: Dict):
    school_class.add_student(student)

    response = client.patch(
        f'/api/v1/school_class/{school_class.id}/student',
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 400
    data = loads(response.data.decode("utf-8"))['message']
    assert data == "Data is not valid!"


def test_patch_update_student_email_exceptions(client: FlaskClient,
                                               mocker: MockFixture,
                                               school_class: SchoolClass,
                                               access_token: List[str],
                                               student: Student):
    school_class.add_student(student)

    def _mock_update_email(*args):
        raise exc.DatabaseError('', '', '')

    mocker.patch.object(Student, 'update_email', _mock_update_email)

    response = client.patch(
        f'/api/v1/school_class/{school_class.id}/student',
        json={
            'old_email': student.email,
            'new_email': 'test@example.com'
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 500


def test_update_school_class_api(client: FlaskClient,
                                 mocker: MockFixture,
                                 school_class: SchoolClass,
                                 access_token: List[str],
                                 update_school_class_param: dict):
    response = client.put(
        f"/api/v1/school_class/{school_class.id}",
        json=update_school_class_param,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )
    school_class.reload()

    assert response.status_code == 200
    assert school_class.name == update_school_class_param["name"]
    assert school_class.year_group == update_school_class_param["year_group"]
    assert school_class.start_date == update_school_class_param["start_date"]


def test_update_school_class_api_with_subject(client: FlaskClient,
                                              mocker: MockFixture,
                                              school_class: SchoolClass,
                                              access_token: List[str],
                                              update_school_class_param: dict):
    update_school_class_param.update({
        'subject': 'Biology'
    })
    response = client.put(
        f"/api/v1/school_class/{school_class.id}",
        json=update_school_class_param,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )
    school_class.reload()

    assert response.status_code == 200
    assert school_class.name == update_school_class_param["name"]
    assert school_class.year_group == update_school_class_param["year_group"]
    assert school_class.start_date == update_school_class_param["start_date"]
    assert school_class.subject.name == update_school_class_param["subject"]


@pytest.mark.parametrize('school_class_id,status', [
    pytest.param(100, 404),
    pytest.param(1, 500)
])
def test_update_school_class_api_exception(client: FlaskClient,
                                           mocker: MockFixture,
                                           school_class: SchoolClass,
                                           school_class_param: dict,
                                           school_class_id: int,
                                           access_token: List[str],
                                           status: int):

    school_class_param["some_field"] = "cnajksnadls"
    response = client.put(
        f"/api/v1/school_class/{school_class_id}",
        json=school_class_param,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert response.status_code == status
