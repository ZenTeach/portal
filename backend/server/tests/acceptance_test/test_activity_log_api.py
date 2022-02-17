from typing import List

import pytest
from flask.testing import FlaskClient
from server.models import ActivityLog, SchoolClass, Teacher
from server.tests.factories import SchoolClassFactory


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture(autouse=True)
def activity_logs_(teacher_: Teacher,
                   school_class: SchoolClass):
    ActivityLog.log(teacher_,
                    'create',
                    'school_class',
                    school_class.id,
                    '')
    for i in range(100):
        ActivityLog.log(teacher_,
                        'update',
                        'school_class',
                        school_class.id,
                        '')


def test_get_activity_logs(client: FlaskClient,
                           school_class: SchoolClass,
                           access_token: List[str]):
    response = client.get(
        '/api/v1/activity_logs',
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    activity_log = ActivityLog.query.all()[0]
    assert response.status_code == 200
    assert response.json[0] == {
        'action': 'create',
        'created': str(activity_log.created.strftime('%Y-%m-%dT%H:%M:%S.%f')),
        'item_type': 'school_class',
        'item_id': school_class.id,
        'note': ''
    }
    assert len(response.json) == 10
