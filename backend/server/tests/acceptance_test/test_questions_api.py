import json
from typing import List, Union

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.tests.factories import QuestionsFactory


@pytest.fixture(autouse=True)
def populate_questions(client: FlaskClient):
    QuestionsFactory.create_batch(5, subject="Physics", topic="testKI",
                                  multiple_choice_question_type=True)
    QuestionsFactory.create_batch(3, subject="Chemistry", topic="anotherKI",
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
    assert len(data["questions"]) == 8


@pytest.mark.parametrize("topics,topic_count,status_code",
                         [pytest.param(["testKI"], 5, 200),
                          pytest.param(["testKI", "anotherKI"], 8, 200)])
def test_knowledge_item_filter(client: FlaskClient,
                               mocker: MockFixture,
                               topics: List[str],
                               topic_count: int,
                               status_code: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/filter/ki",
        json={
            "topics_selected": topics
        }
    )
    data = json.loads(response.data)

    assert response.status_code == status_code
    assert len(data) == topic_count


@pytest.mark.parametrize("topics,error_code", [
                         pytest.param(None, 400),
                         pytest.param([], 404)])
def test_knowledge_item_filter_errors(client: FlaskClient,
                                      mocker: MockFixture,
                                      topics: Union[List[str], None],
                                      error_code: int):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/filter/ki",
        json={
            "topics_selected": topics
        }
    )

    assert response.status_code == error_code


@pytest.mark.parametrize('param,status_code,topics',
                         [pytest.param('chemistry', 200, 13),
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
    assert len(data) == 13
