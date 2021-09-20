import json
from typing import List

import pytest
from factory import build
from flask.testing import FlaskClient
from server.models import KnowledgeItem, Subject, Teacher, Topic
from server.tests.factories import KnowledgeItemFactory, TopicFactory


@pytest.fixture
def math_subject() -> Subject:
    s = Subject(name='Math', enabled=True)
    s.save()
    return s


@pytest.fixture
def biology_subject() -> Subject:
    s = Subject(name='Biology', enabled=True)
    s.save()
    return s


@pytest.fixture
def biology_topic(client: FlaskClient,
                  biology_subject: Subject) -> Topic:
    return TopicFactory(subject_id=biology_subject.id, value='abcd')


@pytest.fixture(autouse=True)
def biology_kis(client: FlaskClient,
                biology_topic: Topic,
                biology_subject: Subject) -> KnowledgeItem:
    return KnowledgeItemFactory.create_batch(5, subject_id=biology_subject.id,
                                             topic_id=biology_topic.id)


@pytest.fixture
def ki_():
    return KnowledgeItem.query.first()


@pytest.fixture
def ki_create_payload(biology_subject: Subject,
                      teacher_: Teacher,
                      biology_topic: Topic) -> dict:
    return build(dict,
                 FACTORY_CLASS=KnowledgeItemFactory,
                 topic_id=biology_topic.id,
                 subject=biology_subject.name,
                 teacher_id=teacher_.id
                 )


@pytest.fixture
def teacher_():
    return Teacher.query.first()


def test_knowledge_item_get_all(client):
    response = client.get('/api/v1/knowledge_items')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 5


def test_knowledge_item_get_one(client):
    response = client.get('/api/v1/knowledge_item/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['value'] is not None

    response = client.get('/api/v1/knowledge_item/100')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert len(data['data']) == 0
    assert data['message'] == "Knowledge Item not found."


def test_knowledge_item_user_create(client: FlaskClient,
                                    teacher_: Teacher,
                                    ki_create_payload: dict,
                                    access_token: List[str]):
    response = client.post(
        '/api/v1/knowledge_items',
        json=ki_create_payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['data']['teacher_id'] == teacher_.id


def test_knowledge_item_update_topic(client: FlaskClient,
                                     access_token: List[str]):
    response = client.put('/api/v1/knowledge_item/1',
                          json={'value': 'New Knowledge Item'},
                          headers={
                              'Authorization': 'Bearer {}'.format(access_token[0]),
                              'X-CSRF-ACCESS-TOKEN': access_token[2]
                          })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['value'] == 'New Knowledge Item'
