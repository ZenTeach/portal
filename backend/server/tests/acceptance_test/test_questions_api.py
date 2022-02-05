import json
from typing import List, Union

import pytest
from faker import Faker
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import (KnowledgeItem, QuestionsSchema, Subject, Teacher,
                           Topic)
from server.models.questions import Questions
from server.tests.factories import (KnowledgeItemFactory, QuestionsFactory,
                                    TeacherFactory, TopicFactory)

fake = Faker()


@pytest.fixture(autouse=True)
def subjects_(client: FlaskClient) -> None:
    for subject in ['Biology', 'Chemistry', 'Physics']:
        Subject(name=subject, enabled=True).save()


@pytest.fixture()
def subject_() -> Subject:
    s = Subject(name='Chemistry', enabled=True)
    s.save()
    return s


@pytest.fixture()
def subject_id(subject_: Subject) -> int:
    return subject_.id


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return TeacherFactory()


@pytest.fixture
def teacher_created_question(client: FlaskClient,
                             subject_: Subject,
                             teacher_: Teacher) -> Questions:
    subject_id = subject_.id
    topic = TopicFactory(value="testKI", subject_id=subject_id)
    kis = KnowledgeItemFactory(subject_id=subject_id, topic_id=topic.id)
    return QuestionsFactory(subject_id=subject_id,
                            user_created=True,
                            knowledge_item=kis,
                            topic=topic,
                            teacher_id=teacher_.id,
                            multiple_choice_question_type=True,
                            with_choices={
                                'choice_count': 4
                            })


@pytest.fixture(autouse=True)
def populate_questions(client: FlaskClient, subject_: Subject):
    subject_id = subject_.id
    topic = TopicFactory(value="testKI", subject_id=subject_id)
    topic_2 = TopicFactory(value="anotherKI", subject_id=subject_id)
    topic_3 = TopicFactory(value="Default Topic", subject_id=subject_id)
    kis = KnowledgeItemFactory(value="Testing value", subject_id=subject_id, topic_id=topic.id)
    kis_2 = KnowledgeItemFactory(value="Another Testing value",
                                 subject_id=subject_id, topic_id=topic_2.id)
    kis_3 = KnowledgeItemFactory(value="Default Knowledge Item",
                                 subject_id=subject_id, topic_id=topic_3.id)

    for _ in range(10):
        QuestionsFactory(subject_id=subject_id,
                         knowledge_item=kis,
                         topic=topic,
                         multiple_choice_question_type=True)
        QuestionsFactory(subject_id=subject_id,
                         knowledge_item=kis_3,
                         topic=topic_3,
                         multiple_choice_question_type=True)

    for _ in range(3):
        QuestionsFactory(subject_id=subject_id,
                         knowledge_item=kis_2,
                         topic=topic_2,
                         multiple_choice_question_type=True)
        QuestionsFactory(subject_id=subject_id,
                         knowledge_item=kis_3,
                         topic=topic_3,
                         multiple_choice_question_type=True)


@pytest.fixture
def question_payload(subject_: Subject) -> dict:
    topic = TopicFactory(value="Test Topic", subject_id=subject_.id)
    kis = KnowledgeItemFactory(value="Test KI", subject_id=subject_.id, topic_id=topic.id)
    built_question = QuestionsFactory(
        subject_id=subject_.id,
        knowledge_item=kis,
        topic=topic,
        multiple_choice_question_type=True)
    return QuestionsSchema().dump(built_question)


@pytest.fixture
def question_payload_as_json(subject_: Subject, teacher_: Teacher) -> dict:
    topic = Topic.query.first()
    ki = topic.knowledge_items[0]
    q = QuestionsFactory(
        knowledge_item=ki,
        topic=topic,
        multiple_choice_question_type=True,
        subject=subject_.name,
        with_choices={
            'choice_count': 4
        })

    question_json = QuestionsSchema().dump(q)
    correct_choice_id = q.choices[0].id
    question_json.update({
        'correct_choice_id': correct_choice_id,
        'topic': topic.value,
        'knowledge_item': ki.value,
        'subject': subject_.name,
        'question_type': q.question_type.name,
    })

    return question_json


@pytest.fixture
def existing_question_payload_as_json() -> dict:
    subject_id = Subject.query.first().id
    topic = Topic.query.first()
    ki = topic.knowledge_items[0]
    q = QuestionsFactory(multiple_choice_question_type=True,
                         subject_id=subject_id,
                         knowledge_item=ki,
                         topic=topic,
                         with_choices={
                             'choice_count': 4,
                         })
    json_dump = QuestionsSchema().dump(q)
    json_dump['choices'][0].update({
        'is_correct_choice': True
    })
    json_dump.update({
        'question_type': q.question_type.name,
    })
    return json_dump


@pytest.fixture
def question_payload_json_without_correct_choice(subject_: Subject, teacher_: Teacher) -> dict:
    topic = Topic.query.first()
    ki = topic.knowledge_items[0]
    q = QuestionsFactory(knowledge_item=ki,
                         topic=topic,
                         multiple_choice_question_type=True,
                         teacher_id=teacher_.id,
                         with_choices={
                             'choice_count': 4
                         })

    dumped_question = QuestionsSchema().dump(q)
    dumped_question.update({
        'topic': topic.value,
        'knowledge_item': ki.value,
        'subject': subject_.name,
        'question_type': q.question_type.name,
    })
    q.delete()
    return dumped_question


@pytest.fixture
def knowledgeitems_() -> List[str]:
    kis = KnowledgeItem.query.with_entities(KnowledgeItem.value).distinct().all()
    return [item for subl in kis for item in subl if item is not None]


@pytest.fixture
def topics_() -> List[str]:
    topics = Topic.query.with_entities(Topic.value).distinct().all()
    return [item for subl in topics for item in subl if item is not None]


@pytest.fixture
def question_query() -> str:
    return Questions.query.first().question


def mock_get_jwt_identity():
    return {
        "role": "Teacher"
    }


@pytest.mark.parametrize("subject,count,status", [
    pytest.param("Chemistry", 26, 200),
    pytest.param("chemistry", 26, 200),
    pytest.param("bcahsj", 0, 400),
    pytest.param("", 0, 200)
])
def test_question_list_get(client: FlaskClient,
                           mocker: MockFixture,
                           subject: str,
                           access_token: List[str],
                           count: int,
                           status: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(
        f"api/v1/question?subject={subject}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == status

    data = json.loads(response.data)
    assert len(data["questions"]) == count


@pytest.mark.parametrize("topics,topic_count,status_code",
                         [pytest.param(["testKI"], 1, 200),
                          pytest.param(["testKI", "anotherKI"], 2, 200)])
def test_knowledge_item_filter(client: FlaskClient,
                               mocker: MockFixture,
                               topics: List[str],
                               access_token: List[str],
                               topic_count: int,
                               status_code: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/filter/ki",
        json={
            "topics_selected": topics
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
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
                                      access_token: List[str],
                                      topics: Union[List[str], None],
                                      error_code: int):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/filter/ki",
        json={
            "topics_selected": topics
        },
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert response.status_code == error_code


@pytest.mark.parametrize('param,status_code,topics',
                         [pytest.param('chemistry', 200, 3),
                          pytest.param('canjas', 400, 0)])
def test_topic_filter(client: FlaskClient,
                      mocker: MockFixture,
                      param: str,
                      status_code: int,
                      access_token: List[str],
                      topics: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(
        f"/api/v1/question/filter/topic/{param}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    data = json.loads(response.data)

    assert response.status_code == status_code
    assert len(data) == topics


@pytest.mark.parametrize('subject', ['chemistry', 'Chemistry'])
def test_topic_filters_with_case_normalization(client: FlaskClient,
                                               mocker: MockFixture,
                                               access_token: List[str],
                                               subject: str):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.get(
        f"/api/v1/question/filter/topic/{subject}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    data = json.loads(response.data)

    assert response.status_code == 200
    assert len(data) == 3


def test_question_create_api(client: FlaskClient,
                             question_payload_as_json: dict,
                             access_token: List[str],
                             mocker: MockFixture):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_payload_as_json['question'] = fake.sentence()
    response = client.post(
        "/api/v1/question",
        json=question_payload_as_json,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 201
    new_question = Questions.query.all()[-1:][0]
    assert new_question.exam_board == question_payload_as_json['exam_board']


def test_question_create_api_question_already_existing(client: FlaskClient,
                                                       question_payload: dict,
                                                       subject_id: Subject,
                                                       access_token: List[str],
                                                       mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    existing_question = Questions.query.first()
    question_payload['subject_id'] = subject_id
    question_payload['tag'] = existing_question.tag
    question_payload['question'] = existing_question.question

    response = client.post("/api/v1/question",
                           json=question_payload,
                           headers={
                               'Authorization': 'Bearer {}'.format(access_token[0]),
                               'X-CSRF-ACCESS-TOKEN': access_token[2]
                           })

    assert response.status_code == 400


def test_question_create_api_empty_data(client: FlaskClient,
                                        access_token: List[str],
                                        mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 400


def test_question_create_api_exception_handling(client: FlaskClient,
                                                question_payload_json_without_correct_choice: dict,
                                                access_token: List[str],
                                                mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_payload_json_without_correct_choice['question'] = fake.sentence()
    del question_payload_json_without_correct_choice['question_type']
    response = client.post(
        "/api/v1/question",
        json=question_payload_json_without_correct_choice,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 500


def test_question_get_item(client: FlaskClient,
                           access_token: List[str],
                           mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question = Questions.query.first()
    response = client.get(
        f"/api/v1/question/{question.id}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["question"]["id"] == question.id


def test_question_delete_api(client: FlaskClient,
                             access_token: List[str],
                             mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question = Questions.query.first()
    response = client.delete(
        f"/api/v1/question/{question.id}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 204


def test_question_delete_api_not_existing_id(client: FlaskClient,
                                             access_token: List[str],
                                             mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    question_id = 10000
    response = client.delete(
        f"/api/v1/question/{question_id}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 400


@pytest.mark.xfail(reason="Broken mock")
def test_question_delete_api_exception_handling(client: FlaskClient,
                                                access_token: List[str],
                                                mocker: MockFixture):
    @mocker.patch("server.db.session.delete")
    def sess_delete_mock(question_object):
        raise Exception()
    question_id = Questions.query.first().id
    response = client.delete(
        f"/api/v1/question/{question_id}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 500


@pytest.mark.parametrize('payload,count', [
    pytest.param({
        "topics": ["testKI"],
        "kis": ["Testing value"]
    }, 10),
    pytest.param({
        "topics": ["testKI"]
    }, 10),
    pytest.param({
        "kis": ["Testing value", "Another Testing value"]
    }, 13)
])
def test_question_filter_by_topics_kis(client: FlaskClient,
                                       mocker: MockFixture,
                                       access_token: List[str],
                                       payload: dict,
                                       count: int):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.post(
        "/api/v1/question/fetch",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

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
                                             access_token: List[str],
                                             payload: dict):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    response = client.post(
        "/api/v1/question/fetch",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 400


def test_question_search_with_params(client: FlaskClient,
                                     mocker: MockFixture,
                                     knowledgeitems_: List[str],
                                     topics_: List[str],
                                     access_token: List[str],
                                     question_query: str):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    payload = {
        "query": question_query,
        "topic": topics_,
        "knowledge_item": knowledgeitems_,
        "subject": 'Chemistry'
    }

    response = client.post(
        "/api/v1/question/search",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) > 0


def test_question_search_with_special_character_params(client: FlaskClient,
                                                       mocker: MockFixture,
                                                       access_token: List[str],
                                                       knowledgeitems_: List[str],
                                                       topics_: List[str]):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    payload = {
        "query": '*',
        "topic": topics_,
        "knowledge_item": knowledgeitems_,
        "subject": 'Chemistry'
    }

    response = client.post(
        "/api/v1/question/search",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) > 0


def test_question_search_optional_filter(client: FlaskClient,
                                         mocker: MockFixture,
                                         knowledgeitems_: List[str],
                                         topics_: List[str],
                                         access_token: List[str],
                                         question_query: str):

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    # test topic filter
    payload = {
        "query": question_query,
        "topic": [],
        "knowledge_item": knowledgeitems_,
        "subject": 'Chemistry'
    }
    response = client.post(
        "/api/v1/question/search",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data['data']) > 0

    # test knowledge item filter
    payload['topic'] = topics_
    payload['knowledge_item'] = []
    response = client.post(
        "/api/v1/question/search",
        json=payload
    )
    data = json.loads(response.data)
    assert response.status_code == 200
    assert len(data['data']) > 0


def test_question_search_subject_filter(client: FlaskClient,
                                        mocker: MockFixture,
                                        knowledgeitems_: List[str],
                                        topics_: List[str],
                                        access_token: List[str],
                                        question_query: str):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    payload = {
        "query": question_query,
        "topic": topics_,
        "knowledge_item": knowledgeitems_,
        "subject": ''
    }
    response = client.post(
        "/api/v1/question/search",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )
    assert response.status_code == 404


def test_question_search_empty_query(client: FlaskClient,
                                     mocker: MockFixture,
                                     knowledgeitems_: List[str],
                                     topics_: List[str],
                                     access_token: List[str],
                                     question_query: str):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    payload = {
        "query": '',
        "topic": topics_,
        "knowledge_item": knowledgeitems_,
        "subject": 'Chemistry'
    }
    response = client.post(
        "/api/v1/question/search",
        json=payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        }
    )
    assert response.status_code == 400


def test_teacher_owned_question_get_action(client: FlaskClient,
                                           mocker: MockFixture,
                                           teacher_identity: Teacher,
                                           access_token: List[str]):
    teacher_identity.questions.append(Questions.query.first())
    teacher_identity.save()

    response = client.get(
        "/api/v1/question/user_created",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['questions']) == 1


def test_teacher_owned_question_create_action(client: FlaskClient,
                                              mocker: MockFixture,
                                              teacher_identity: Teacher,
                                              access_token: List[str],
                                              question_payload_as_json: dict):
    def mocked_log_activity(*args):
        assert len(args) == 5
    mocker.patch('server.api.questions_api.log_activity', mocked_log_activity)

    question_payload_as_json.update({
        'user_created': True,
        'teacher_id': teacher_identity.id
    })

    response = client.post(
        "/api/v1/question/user_created",
        json=question_payload_as_json,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 201
    teacher_identity.reload()
    question = teacher_identity.questions[0]

    assert len(teacher_identity.questions) > 0
    assert question.user_created
    assert len(question.choices) > 0
    assert all([choice.user_created for choice in question.choices])  # noqa
    assert question.correct_choice() is not None


def test_teacher_owned_question_create_action_422_error(client: FlaskClient,
                                                        mocker: MockFixture,
                                                        teacher_: Teacher,
                                                        teacher_identity: Teacher,
                                                        access_token: List[str],
                                                        question_payload_as_json: dict):
    question_payload_as_json.update({
        'user_created': True,
        'teacher_id': teacher_.id
    })
    response = client.post(
        "/api/v1/question/user_created",
        json=question_payload_as_json,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 422
    assert response.data


def test_teacher_owned_question_delete_action(client: FlaskClient,
                                              mocker: MockFixture,
                                              access_token: List[str],
                                              teacher_identity: Teacher,
                                              teacher_created_question: Questions) -> None:
    def mocked_log_activity(*args):
        assert len(args) == 5
    mocker.patch('server.api.questions_api.log_activity', mocked_log_activity)

    teacher_created_question.teacher_id = teacher_identity.id
    teacher_created_question.save()
    response = client.delete(
        f"/api/v1/question/user_created/{teacher_created_question.id}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 204


def test_teacher_owned_question_update_action(client: FlaskClient,
                                              teacher_identity: Teacher,
                                              mocker: MockFixture,
                                              access_token: List[str],
                                              teacher_created_question: Questions) -> None:
    def mocked_log_activity(*args):
        assert len(args) == 5
    mocker.patch('server.api.questions_api.log_activity', mocked_log_activity)

    update_params = {
        'knowledge_item': "Another Testing value"
    }
    teacher_created_question.teacher_id = teacher_identity.id
    teacher_created_question.save()
    response = client.patch(
        f"/api/v1/question/user_created/{teacher_created_question.id}",
        json=update_params,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    question = teacher_identity.questions[0]
    assert response.status_code == 200
    assert question.correct_choice() is not None
    assert all([choice.user_created for choice in question.choices])  # noqa
    assert question.correct_choice().id in list(map(lambda choice: choice.id, question.choices))


def test_teacher_owned_question_update_choices_action(client: FlaskClient,
                                                      teacher_identity: Teacher,
                                                      mocker: MockFixture,
                                                      access_token: List[str],
                                                      teacher_created_question: Questions) -> None:
    def mocked_log_activity(*args):
        assert len(args) == 5
    mocker.patch('server.api.questions_api.log_activity', mocked_log_activity)

    update_params = {
        'knowledge_item': "Another Testing value",
        'choices': [
            {
                "feedback": "choice 1 feedback",
                "is_correct_choice": False,
                "uuid": teacher_created_question.choices[0].uuid,
                "value": "choice 1",
                "weight": 1
            },
            {
                "feedback": "choice 2 feedback",
                "is_correct_choice": False,
                "uuid": teacher_created_question.choices[1].uuid,
                "value": "choice 2",
                "weight": 1
            },
            {
                "feedback": "choice 3 feedback",
                "is_correct_choice": False,
                "uuid": teacher_created_question.choices[2].uuid,
                "value": "choice 3",
                "weight": 1
            },
            {
                "feedback": "choice 4 feedback",
                "is_correct_choice": True,
                "uuid": teacher_created_question.choices[3].uuid,
                "value": "choice 4",
                "weight": 1
            },
        ]
    }
    teacher_created_question.teacher_id = teacher_identity.id
    teacher_created_question.save()
    response = client.patch(
        f"/api/v1/question/user_created/{teacher_created_question.id}",
        json=update_params,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    question = teacher_identity.questions[0]
    assert response.status_code == 200
    assert all([choice.user_created for choice in question.choices])
    assert question.correct_choice() is not None
    assert question.correct_choice().value == 'choice 4'
    assert question.correct_choice().id in list(map(lambda choice: choice.id, question.choices))


def test_updating_original_question_creates_question_on_user(client: FlaskClient,
                                                             mocker: MockFixture,
                                                             access_token: List[str],
                                                             teacher_identity: Teacher,
                                                             existing_question_payload_as_json: dict) -> None:  # noqa
    existing_question_payload_as_json['subject'] = existing_question_payload_as_json['subject']['name']  # noqa
    existing_question_payload_as_json['topic'] = existing_question_payload_as_json['topic']['value']  # noqa
    existing_question_payload_as_json['knowledge_item'] = existing_question_payload_as_json['knowledge_item']['value']  # noqa
    assert Questions.query.filter_by(teacher_id=teacher_identity.id).count() == 0

    def mocked_log_activity(*args):
        assert len(args) == 5
    mocker.patch('server.api.questions_api.log_activity', mocked_log_activity)

    q_id = existing_question_payload_as_json.pop('id')
    existing_question_payload_as_json.update({
        'teacher_id': teacher_identity.id
    })
    response = client.patch(
        f"/api/v1/question/user_created/{q_id}",
        json=existing_question_payload_as_json,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 201
    assert Questions.query.filter_by(teacher_id=teacher_identity.id).count() == 1
