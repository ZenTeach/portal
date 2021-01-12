import json
from typing import Dict

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import ClassQuiz, QuestionsSchema, SchoolClass
from server.tests.factories import ClassQuizFactory, QuestionsFactory


@pytest.fixture
def classquiz_params(school_class: SchoolClass) -> Dict:  # noqa
    questions = QuestionsFactory.create_batch(5, multiple_choice_question_type=True, with_choices=4)  # noqa
    dumper = QuestionsSchema()
    questions = [dumper.dump(question) for question in questions]

    return build(dict, FACTORY_CLASS=ClassQuizFactory, class_id=school_class.id, questions=questions)  # noqa


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


def dummy_jwt_identity() -> Dict:
    return {
        'identity': {
            'email': 'dummy@example.com'
        }
    }


def mock_jwt_required() -> bool:
    return True


def test_classquiz_create_api(client: FlaskClient,
                              classquiz_params: Dict,
                              mocker: MockFixture):
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


def test_classquiz_create_api_with_no_question_fails(client: FlaskClient,
                                                     classquiz_params: Dict,
                                                     mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    classquiz_params.pop('questions')
    response = client.post(
        "/api/v1/class_quiz",
        json=classquiz_params,
    )

    assert response.status_code == 400


def test_classquiz_get_api(client: FlaskClient,
                           classquiz_: ClassQuiz):

    response = client.get(f'/api/v1/class_quiz/{classquiz_.uuid}')

    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['data']['subject'] in ['Chemistry', 'Biology', 'Physics']
