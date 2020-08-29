import json

import pytest
from factory import build
from server.tests.factories import SchoolClassFactory


@pytest.fixture
def school_class(teacher):
    return SchoolClassFactory.create(teacher_id=teacher.id)


def test_school_class_ping(client):
    response = client.get("/api/v1/school_class/ping")

    data = json.loads(response.data.decode())
    assert response.status_code, 200
    assert data == {"status": "success", "message": "Pinged school class"}


def test_get_school_class_with_id(client, student, school_class, mocker):
    school_class.add_student(student)
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get("/api/v1/school_class/{}".format(school_class.id))

    assert response.status_code == 200

    data = json.loads(response.data.decode())["data"]

    assert data["id"] == school_class.id
    assert data["students"][0]["id"] == student.id


@pytest.mark.skip("Temporarily skipped")
def test_create_school_class(client, mocker, teacher, student):
    new_class = build(dict, FACTORY_CLASS=SchoolClassFactory)

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    @mocker.patch('server.api.school_class_api.get_jwt_identity')
    def mock_identity():
        return {
            'identity': {
                'id': teacher.id,
                'email': teacher.email
            }
        }
    response = client.post(
        "/api/v1/school_class",
        json={
            "name": new_class["name"],
            "subject": new_class["subject"],
            "start_date": str(new_class["start_date"]),
        }
    )

    assert response.status_code == 201
    data = json.loads(response.data.decode())["data"]
    assert data == {
        "status": "success",
        "message": "{} was added!".format(new_class["name"]),
    }


def test_fetch_school_class_list(client, mocker):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    SchoolClassFactory.create_batch(5)

    response = client.get("/api/v1/school_class")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data["data"]["school_classes"]) == 5


def test_delete_school_class(client, mocker, school_class):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.delete(f'/api/v1/school_class/{school_class.id}')

    assert response.status_code == 204
