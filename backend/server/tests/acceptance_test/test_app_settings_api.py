from flask.testing import FlaskClient


def test_get_setting(client: FlaskClient) -> None:
    """
        Test that the settings endpoint returns the correct settings.
    """

    response = client.get('api/v1/settings')

    assert response.status_code == 200
