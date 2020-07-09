import time

import pytest
from server.api.oauth_api import OAuth2Authorize
from server.models import OAuth2Client
from werkzeug.security import gen_salt


@pytest.fixture(scope='function')
def oauth2_client(teacher, dbsession):
    client = OAuth2Client(
        client_id=gen_salt(24),
        client_id_issued_at=int(time.time()),
        user_id=teacher.id,
    )
    client_metadata = {
        "client_name": "test_client",
        "client_uri": "https://localhost:5001/",
        "grant_types": ['authorization_code', 'password'],
        "redirect_uris": ["https://localhost:5001/oauth_callback"],
        "response_types": ['code'],
        "scope": ['profile'],
        "token_endpoint_auth_method": ['client_secret_basic']
    }
    client.client_secret = gen_salt(48)
    client.set_client_metadata(client_metadata)
    client.save()
    return client


def test_get_oauth2_authorize_endpoint(client):
    pass


@pytest.skip("Fix test")
def test_post_oauth2_authorize_endpoint(client, mocker, teacher, monkeypatch, oauth2_client):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    def mock_teacher(*args, **kwargs):
        return teacher
    monkeypatch.setattr(OAuth2Authorize, "get_user", mock_teacher)
    response = client.post(
        "/oauth/authorize",
        json={
            "confirmation": "Yes"
        })
    print("JSON response:")
    # import pdb; pdb.set_trace()
    # print(response.get_json())
    assert response.status_code == 200


@pytest.skip("Unfinished")
def test_oauth2_token_endpoint(client, oauth_client, teacher):
    client_secret = oauth_client.client_secret  # noqa
    client_id = oauth_client.client_id  # noqa

    response = client.post(  # noqa
        "/oauth/token"
    )
