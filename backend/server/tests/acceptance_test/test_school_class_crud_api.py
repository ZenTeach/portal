import json

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import SchoolClass, Teacher
from server.models.student import Student
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def student() -> Student:
    return StudentFactory.create()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def school_class_param(teacher_: Teacher) -> dict:
    return build(dict, FACTORY_CLASS=SchoolClassFactory, teacher_id=teacher_.id)


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
                                  mocker: MockFixture):
    school_class.add_student(student)
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get("/api/v1/school_class/{}".format(school_class.id))

    assert response.status_code == 200

    data = json.loads(response.data.decode())["data"]

    assert data["id"] == school_class.id
    assert data["students"][0]["id"] == student.id


def test_create_school_class(client: FlaskClient,
                             mocker: MockFixture,
                             mock_identity: dict,
                             school_class_param: dict):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.school_class_api.get_jwt_identity', return_value=mock_identity)

    response = client.post(
        "/api/v1/school_class",
        json=school_class_param
    )

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data == {
        "status": "success",
        "message": "{} was added!".format(school_class_param["name"]),
    }


def test_fetch_school_class_list(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    SchoolClassFactory.create_batch(5)

    response = client.get("/api/v1/school_class")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data["data"]["school_classes"]) == 5


def test_delete_school_class(client: FlaskClient,
                             mocker: MockFixture,
                             school_class: SchoolClass):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.delete(f'/api/v1/school_class/{school_class.id}')

    assert response.status_code == 204


def test_add_student_to_school_class(client: FlaskClient,
                                     mocker: MockFixture,
                                     school_class: SchoolClass):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    student_payload = {
        'firstname': 'Michael',
        'lastname': 'Scott',
        'email': 'mscott@dunder-mifflin.com'
    }

    response = client.post(
        f'/api/v1/school_class/{school_class.id}/student',
        json=student_payload
    )

    assert len(school_class.students) == 1
    assert response.status_code == 201


def test_remove_student_from_school_class(client: FlaskClient,
                                          mocker: MockFixture,
                                          school_class: SchoolClass,
                                          student: Student):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    school_class.add_student(student)

    assert len(school_class.students) != 0

    response = client.delete(
        f'/api/v1/school_class/{school_class.id}/student?student_id={student.id}')

    assert response.status_code == 204
    assert len(school_class.students) == 0


def test_update_school_class_api(client: FlaskClient,
                                 mocker: MockFixture,
                                 school_class: SchoolClass,
                                 school_class_param: dict):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.put(
        f"/api/v1/school_class/{school_class.id}",
        json=school_class_param
    )
    school_class.reload()

    assert response.status_code == 200
    assert school_class.subject == school_class_param["subject"]
    assert school_class.name == school_class_param["name"]
    assert school_class.year_group == school_class_param["year_group"]
    assert school_class.start_date == school_class_param["start_date"]


@pytest.mark.parametrize('school_class_id,status', [
    pytest.param(100, 404),
    pytest.param(1, 500)
])
def test_update_school_class_api_exception(client: FlaskClient,
                                           mocker: MockFixture,
                                           school_class: SchoolClass,
                                           school_class_param: dict,
                                           school_class_id: int,
                                           status: int):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    school_class_param["some_field"] = "cnajksnadls"
    response = client.put(
        f"/api/v1/school_class/{school_class_id}",
        json=school_class_param
    )

    assert response.status_code == status
