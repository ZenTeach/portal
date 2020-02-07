import json
import pytest
# import
def test_stats_api_ping(client):
    response = client.get('/api/v1/stats/ping')
    data = json.loads(response.data.decode())
    assert response.status_code, 200
    assert data == {
        "status": "success",
        "message": "Pinged the stats api"
    }

# mock the get_jwt_identity method
# TODO: Finalize this
def get_jwt_identity_mock(mock_, teacher):
    from server.models import TeacherSchema
    dumper = TeacherSchema()
    return { 'identity': dumper.dump(teacher)}

def jwt_required_mocker():
    return True

def with_required_roles_mocker():
    return True

# @pytest.mock("server.api.stats_api.")
def test_administered_quiz_stat(client, mocker):
    # mock jwt token checking
    mocker.patch.multiple("server.api.stats_api", jwt_required=jwt_required_mocker, with_required_roles=with_required_roles_mocker)
    mocker.patch('server.api.stats_api.get_jwt_identity', new=get_jwt_identity_mock)
    response = client.get('/api/v1/stats/correct_response')
    # assert

