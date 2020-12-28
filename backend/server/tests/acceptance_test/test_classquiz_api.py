import json

import pytest
from factory import build
from server.models import ClassQuiz
from server.tests.factories import ClassQuizFactory


@pytest.fixture
def classquiz_params(school_class):
    return build(dict, FACTORY_CLASS=ClassQuizFactory, class_id=school_class.id)


@pytest.fixture
def classquiz_(school_class):
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


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

    assert response.status_code == 201
    cq = ClassQuiz.query.first()

    assert cq.url is not None


def test_classquiz_get_api(client, classquiz_, school_class):

    response = client.get(f'/api/v1/class_quiz/{classquiz_.uuid}')

    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['data']['subject'] in ['Chemistry', 'Biology', 'Physics']
