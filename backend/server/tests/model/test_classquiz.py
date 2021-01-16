import re

import pytest
from flask.testing import FlaskClient
from server.models import (ClassQuiz, ClassQuizStatus, QuestionsSchema,
                           SchoolClass)
from server.tests.factories import (ClassQuizFactory, QuestionsFactory,
                                    SchoolClassFactory)


@pytest.fixture
def _class(client: FlaskClient) -> SchoolClass:
    return SchoolClassFactory.create()


@pytest.fixture
def classquiz_(client: FlaskClient, _class: SchoolClass):
    cq = ClassQuizFactory.create(class_id=_class.id, with_multiple_choice_questions=4)
    return cq


@pytest.fixture
def classquiz_with_questions(client: FlaskClient, _class: SchoolClass) -> ClassQuiz:
    # questions = []
    # for _ in range(5):
    #     questions.append(QuestionsFactory.create(multiple_choice_question_type=True, with_choices=4, weight=1))  # noqa

    questions = QuestionsFactory.create_batch(5, multiple_choice_question_type=True, with_choices=4, weight=1)  # noqa
    dumper = QuestionsSchema()
    questions = [dumper.dump(question) for question in questions]
    return ClassQuizFactory.create(class_id=_class.id, questions=questions)


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


def test_classquiz_max_score_is_set(client: FlaskClient, classquiz_with_questions: ClassQuiz):
    assert classquiz_with_questions.max_score is not None
    assert classquiz_with_questions.max_score > 0
