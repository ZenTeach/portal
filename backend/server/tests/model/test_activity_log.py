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


def test_activity_log_log(client: FlaskClient,
                          school_class: SchoolClass,
                          teacher_: Teacher):
    ActivityLog.log(teacher_,
                    'create', 'school_class',
                    school_class.id,
                    {},
                    'Imported from CSV')

    assert teacher_.activity_logs.count() == 1
