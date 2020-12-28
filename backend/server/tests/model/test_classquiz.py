import re

import pytest
from flask.testing import FlaskClient
from server.models import ClassQuiz, ClassQuizStatus
from server.tests.factories import ClassQuizFactory, SchoolClassFactory


@pytest.fixture
def classquiz_(client: FlaskClient):
    _class = SchoolClassFactory.create()
    cq = ClassQuizFactory.create(class_id=_class.id)
    return cq


def test_classquiz_set_url(client: FlaskClient):
    _class = SchoolClassFactory.create()
    quiz_instance = ClassQuizFactory.create(class_id=_class.id)
    regex = r'^http:\/\/local.*8080\/quiz_view\/([0-9a-z-]*)'
    extracted_uuid = re.findall(regex, quiz_instance.url)[0]

    assert quiz_instance.uuid is not None
    assert re.match(regex, quiz_instance.url) is not None
    assert extracted_uuid == str(quiz_instance.uuid)
    assert quiz_instance.status == ClassQuizStatus.created


def test_classquiz_update_status(client: FlaskClient, classquiz_: ClassQuiz):
    assert classquiz_.status == ClassQuizStatus.created

    classquiz_.reload()
    classquiz_.update_status(ClassQuizStatus.in_progress)

    assert classquiz_.status == ClassQuizStatus.in_progress


def test_classquiz_max_score_is_set(client: FlaskClient, classquiz_: ClassQuiz):
    assert classquiz_.max_score is not None
    assert classquiz_.max_score > 0
