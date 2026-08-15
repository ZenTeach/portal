import json

import pytest
from server.models import Teacher


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


def test_stats_api_ping(client):
    response = client.get("/api/v1/stats/ping")
    data = json.loads(response.content.decode())
    assert response.status_code, 200
    assert data == {"status": "success", "message": "Pinged the stats api"}


# mock the get_jwt_identity method
# TODO: Finalize this


def get_jwt_identity_mock(mock_, teacher_):
    from server.models import TeacherSchema

    return {"identity": TeacherSchema.dump_one(teacher_)}


def jwt_required_mocker():
    return True


def with_required_roles_mocker():
    return True


# @pytest.mock("server.routers.stats.")

@pytest.mark.skip("Broken mock")
def test_administered_quiz_stat(client, mocker):
    # mock jwt token checking
    mocker.patch.multiple(
        "server.routers.stats",
        jwt_required=jwt_required_mocker,
        with_required_roles=with_required_roles_mocker,
    )
    mocker.patch("server.routers.stats.get_jwt_identity",
                 new=get_jwt_identity_mock)
    response = client.get("/api/v1/stats/correct_response")  # noqa
    # assert
