import json

import pytest
from factory import build
from server.models import Subject, Teacher, Topic
from server.tests.factories import TopicFactory


@pytest.fixture
def subject_():
    s = Subject(name='Math', enabled=True)
    s.save()
    return s


@pytest.fixture(autouse=True)
def topics(client, subject_):
    TopicFactory.create_batch(3, subject_id=subject_.id)


@pytest.fixture
def searchable_topic(client, subject_):
    return TopicFactory(subject_id=subject_.id, value='Searchable Topic')


@pytest.fixture
def topic_():
    return Topic.query.first()


@pytest.fixture
def teacher_():
    return Teacher.query.first()


@pytest.fixture
def topic_create_payload(subject_, teacher_):
    return build(dict,
                 FACTORY_CLASS=TopicFactory,
                 subject=subject_.name,
                 teacher_id=teacher_.id
                 )


def test_topic_get_all(client):
    response = client.get('/api/v1/topics')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 3


def test_topic_get_one(client):
    response = client.get('/api/v1/topic/1')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['value'] is not None

    response = client.get('/api/v1/topic/100')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert len(data['data']) == 0
    assert data['message'] == "Topic not found."


def test_topic_user_create(client, teacher_, topic_create_payload, access_token):
    response = client.post(
        '/api/v1/topics',
        json=topic_create_payload,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['data']['teacher_id'] == teacher_.id


def test_topic_update_topic(client, access_token):
    response = client.put('/api/v1/topic/1',
                          json={'value': 'New Topic'},
                          headers={
                              'Authorization': 'Bearer {}'.format(access_token[0]),
                              'X-CSRF-ACCESS-TOKEN': access_token[2]
                          })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['value'] == 'New Topic'


def test_topic_full_text_search(client, searchable_topic, access_token):
    response = client.post(
        '/api/v1/topics/search',
        json={'search': 'search'},
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 1
    assert data['data'][0]['value'] == searchable_topic.value
