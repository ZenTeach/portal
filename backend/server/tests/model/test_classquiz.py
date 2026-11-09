import re

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import (ClassQuiz, ClassQuizStatus, KnowledgeItem,
                           QuestionsSchema, SchoolClass, Subject, Topic)
from server.tests.factories import (ClassQuizFactory, KnowledgeItemFactory,
                                    QuestionsFactory, SchoolClassFactory,
                                    SubjectFactory, TopicFactory)


@pytest.fixture
def subject_() -> Subject:
    return SubjectFactory(name="Chemistry")


@pytest.fixture
def _class(client: FlaskClient) -> SchoolClass:
    return SchoolClassFactory.create()


@pytest.fixture
def classquiz_(client: FlaskClient, _class: SchoolClass):
    cq = ClassQuizFactory.create(class_id=_class.id, with_multiple_choice_questions=4)
    return cq


@pytest.fixture
def classquiz_private_(client: FlaskClient, _class: SchoolClass):
    cq = ClassQuizFactory.create(class_id=_class.id, private=True,
                                 with_multiple_choice_questions=4)
    return cq


@pytest.fixture
def topic_(subject_: Subject) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def knowledge_item(client: FlaskClient,
                   subject_: Subject,
                   topic_: Topic) -> KnowledgeItem:
    return KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic_.id)


@pytest.fixture
def classquiz_with_questions(client: FlaskClient,
                             _class: SchoolClass,
                             topic_: Topic,
                             knowledge_item: KnowledgeItem) -> ClassQuiz:
    questions = QuestionsFactory.create_batch(5,
                                              multiple_choice_question_type=True,
                                              knowledge_item=knowledge_item,
                                              topic=topic_,
                                              with_choices={
                                                  'knowledge_item': knowledge_item
                                              })
    questions = [QuestionsSchema.dump_one(question) for question in questions]
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


def test_classquiz_set_defaultname(client: FlaskClient,
                                   classquiz_: ClassQuiz):
    old_name = classquiz_.name
    classquiz_.name = classquiz_.set_default_quizname()
    classquiz_.save(refresh=True)
    assert classquiz_.name != old_name


def test_classquiz_set_defaultname_with_exception(client: FlaskClient,
                                                  classquiz_: ClassQuiz,
                                                  mocker: MockFixture):
    @mocker.patch('server.models.ClassQuiz.query.filter_by')
    def mocked_filter_by():
        raise Exception('Some dummy exception')
    old_name = classquiz_.name
    with pytest.raises(Exception):
        classquiz_.name = classquiz_.set_default_quizname()
        classquiz_.save(refresh=True)
        assert classquiz_.name != old_name
        assert classquiz_.name == "Default Quiz Name"


def test_classquiz_update_status(client: FlaskClient, classquiz_: ClassQuiz):
    assert classquiz_.status == ClassQuizStatus.created

    classquiz_.reload()
    classquiz_.update_status(ClassQuizStatus.in_progress)

    assert classquiz_.status == ClassQuizStatus.in_progress


def test_classquiz_max_score_is_set(client: FlaskClient, classquiz_with_questions: ClassQuiz):
    assert classquiz_with_questions.max_score is not None
    assert classquiz_with_questions.max_score > 0
    assert classquiz_with_questions.max_score == len(classquiz_with_questions.questions)


def test_classquiz_private_type(client: FlaskClient, classquiz_private_: ClassQuiz):
    assert classquiz_private_.private is not None
    assert classquiz_private_.private
