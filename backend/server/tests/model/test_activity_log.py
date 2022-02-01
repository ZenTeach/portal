import pytest
from flask.testing import FlaskClient
from server.models import ActivityLog, Teacher


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


def test_activity_log_log(client: FlaskClient, teacher_: Teacher):
    ActivityLog.log(teacher_,
                    'create', 'school_class', 1,
                    'Imported from CSV')

    assert teacher_.activity_logs.count() == 1
