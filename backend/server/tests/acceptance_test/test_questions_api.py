import json

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import Questions
from server.tests.factories import QuestionsFactory


@pytest.fixture(autouse=True)
def populate_questions(client: FlaskClient):
    QuestionsFactory.create_batch(5, subject="Physics", topic="testKI",
                                  multiple_choice_question_type=True)
    QuestionsFactory.create_batch(5, subject="Chemistry", multiple_choice_question_type=True)
    QuestionsFactory.create_batch(5, subject="chemistry", multiple_choice_question_type=True)


def mock_get_jwt_identity():
    return {
        "role": "Teacher"
    }


def test_question_list_get(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get("api/v1/question?subject=Chemistry")

    assert response.status_code == 200

    data = json.loads(response.data)
    assert len(data["questions"]) == 5


def test_knowledge_item_filter(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get("/api/v1/question/filter/ki/testKI")
    data = json.loads(response.data)
    kis = Questions.query.with_entities(Questions.knowledge_item)\
        .filter_by(topic="testKI")\
        .count()

    assert response.status_code == 200
    assert len(data) == kis


@pytest.mark.parametrize('param,status_code,topics',
                         [pytest.param('chemistry', 200, 10),
                          pytest.param('canjas', 200, 0)])
def test_topic_filter(client: FlaskClient,
                      mocker: MockFixture,
                      param: str,
                      status_code: int,
                      topics: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(f"/api/v1/question/filter/topic/{param}")
    data = json.loads(response.data)

    assert response.status_code == status_code
    assert len(data) == topics


@pytest.mark.parametrize('subject', ['chemistry', 'Chemistry'])
def test_topic_filters_with_case_normalization(client: FlaskClient,
                                               mocker: MockFixture,
                                               subject: str):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(f"/api/v1/question/filter/topic/{subject}")

    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 10
