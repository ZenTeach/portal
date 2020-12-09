import json
from random import choice
from typing import List, Union

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import QuestionsSchema
from server.models.questions import Questions
from server.tests.factories import QuestionsFactory


@pytest.fixture(autouse=True)
def populate_questions(client: FlaskClient):
    QuestionsFactory.create_batch(5, subject="Physics", topic="testKI",
                                  multiple_choice_question_type=True)
    QuestionsFactory.create_batch(5, subject="Physics", topic="testKI",
                                  knowledge_item="Testing value",
                                  multiple_choice_question_type=True)
    QuestionsFactory.create_batch(3, subject="Chemistry", topic="anotherKI",
                                  multiple_choice_question_type=True)
    QuestionsFactory.create_batch(5, subject="Chemistry", multiple_choice_question_type=True)
    QuestionsFactory.create_batch(5, subject="chemistry", multiple_choice_question_type=True)


@pytest.fixture
def question_payload():
    built_question = QuestionsFactory.build(multiple_choice_question_type=True)
    return QuestionsSchema().dump(built_question)


def mock_get_jwt_identity():
    return {
        "role": "Teacher"
    }


@pytest.mark.parametrize("subject,count,status", [
    pytest.param("Chemistry", 13, 200),
    pytest.param("chemistry", 13, 200),
    pytest.param("bcahsj", 0, 200),
    pytest.param("", 0, 200)
])
def test_question_list_get(client: FlaskClient,
                           mocker: MockFixture,
                           subject: str,
                           count: int,
                           status: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(f"api/v1/question?subject={subject}")

    assert response.status_code == status

    data = json.loads(response.data)
    assert len(data["questions"]) == count


@pytest.mark.parametrize("topics,topic_count,status_code",
                         [pytest.param(["testKI"], 10, 200),
                          pytest.param(["testKI", "anotherKI"], 13, 200)])
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


def test_question_create_api(client: FlaskClient,
                             question_payload: dict,
                             mocker: MockFixture):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_payload['correct_choice_id'] = choice([1, 2, 3, 4])
    response = client.post("/api/v1/question",
                           json=question_payload)

    assert response.status_code == 201


def test_question_create_api_question_already_existing(client: FlaskClient,
                                                       question_payload: dict,
                                                       mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    existing_question = Questions.query.first()
    question_payload['subject'] = existing_question.subject
    question_payload['tag'] = existing_question.tag
    question_payload['question'] = existing_question.question

    response = client.post("/api/v1/question", json=question_payload)

    assert response.status_code == 400


def test_question_create_api_empty_data(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post("/api/v1/question")

    assert response.status_code == 400


def test_question_create_api_exception_handling(client: FlaskClient,
                                                question_payload: dict,
                                                mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_payload["correct_choice_id"] = None
    response = client.post("/api/v1/question", json=question_payload)
    assert response.status_code == 500


def test_question_get_item(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question = Questions.query.first()
    response = client.get(f"/api/v1/question/{question.id}")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["question"]["id"] == question.id


def test_question_delete_api(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question = Questions.query.first()
    response = client.delete(f"/api/v1/question/{question.id}")

    assert response.status_code == 204


def test_question_delete_api_not_existing_id(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_id = 10000
    response = client.delete(f"/api/v1/question/{question_id}")

    assert response.status_code == 400


@pytest.mark.xfail(reason="Broken mock")
def test_question_delete_api_exception_handling(client: FlaskClient, mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch("server.db.session.delete", lambda e: Exception(""))
    question_id = Questions.query.first().id
    response = client.delete(f"/api/v1/question/{question_id}")

    assert response.status_code == 500


@pytest.mark.parametrize('payload,count', [
    pytest.param({
        "topics": ["testKI"],
        "kis": ["Testing value"]
    }, 5),
    pytest.param({
        "topics": ["testKI"]
    }, 10),
    pytest.param({
        "kis": ["Testing value"]
    }, 5)
])
def test_question_filter_by_topics_kis(client: FlaskClient,
                                       mocker: MockFixture,
                                       payload: dict,
                                       count: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.post(
        "/api/v1/question/fetch",
        json=payload)

    data = json.loads(response.data)
    data = data['data']

    assert response.status_code == 200
    assert len(data) == count


@pytest.mark.parametrize("payload", [
    pytest.param({
        "topics": [],
        "kis": []
    }),
    pytest.param({})
])
def test_question_filter_by_topics_kis_error(client: FlaskClient,
                                             mocker: MockFixture,
                                             payload: dict):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/fetch",
        json=payload)

    assert response.status_code == 400
