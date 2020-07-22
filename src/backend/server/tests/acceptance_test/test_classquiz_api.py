import pytest
from factory import build
from server.tests.factories import ClassQuizFactory


@pytest.fixture
def classquiz_params(school_class):
    return build(dict, FACTORY_CLASS=ClassQuizFactory, class_id=school_class.id)


def dummy_jwt_identity():
    return {
        'identity': {
            'email': 'dummy@example.com'
        }
    }


def mock_jwt_required():
    return True


def test_classquiz_create_api(client, classquiz_params, mocker, monkeypatch):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    response = client.post(
        "/api/v1/class_quiz",
        json=classquiz_params,
    )

    assert response.status, 201
