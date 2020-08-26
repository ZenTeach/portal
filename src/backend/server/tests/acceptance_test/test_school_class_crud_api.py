import json

import pytest
from server.tests.factories import SchoolClassFactory


def test_school_class_ping(client):
    response = client.get("/api/v1/school_class/ping")

    data = json.loads(response.data.decode())
    assert response.status_code, 200
    assert data == {"status": "success", "message": "Pinged school class"}


# @pytest.mark.skip
# @pytest.mark.parameterized("teacher__password", ["Asdfgh12!"])
# @pytest.mark.parameterized("school_class__teacher_id",
# [LazyFixture(lambda teacher: teacher.id)])
# @pytest.mark.parameterized("class_quiz__class_id", [school_class.id])


def test_get_school_class_with_id(client,
                                  teacher, student,
                                  school_class, mocker):
    # school_class.add_student(student)
    # school_class.save()
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get("/api/v1/school_class/{}".format(school_class.id))
    assert response.status_code == 200
    data = json.loads(response.data.decode())["data"]
    assert data["id"] == school_class.id
    # assert data["students"][0]["id"] == student.id


@pytest.mark.skip("Broken mock")
def test_add_school_class(client, mocker, teacher, student):
    new_class = SchoolClassFactory.build()
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/school_class",
        json=json.dumps(
            {
                "name": new_class.name,
                "subject": new_class.subject,
                "start_date": str(new_class.start_date),
                "student_id": student.id,
            }
        ),
    )

    assert response.status_code == 201
    data = json.loads(response.data.decode())["data"]
    assert data == {
        "status": "success",
        "message": "{} was added!".format(new_class.name),
    }


@pytest.mark.skip("Temporarily skipped")
def test_fetch_school_class_list(client):
    SchoolClassFactory.create_batch(5)
    response = client.get("/api/v1/school_class")
    assert response.status, 200
    data = json.loads(response.data)
    assert len(data["data"]["school_classes"]) == 5
