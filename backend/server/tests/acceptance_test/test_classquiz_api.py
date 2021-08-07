import json
from typing import Dict, List
from uuid import uuid4

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import (ClassQuiz, KnowledgeItem, QuestionsSchema,
                           QuizGrade, SchoolClass, Student, Subject, Teacher)
from server.tests.factories import (ClassQuizFactory, KnowledgeItemFactory,
                                    QuestionsFactory, QuizGradeFactory,
                                    SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def subject_() -> Subject:
    s = Subject(name="Chemistry", enabled=True)
    s.save()
    return s


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def knowledge_item_() -> KnowledgeItem:
    return KnowledgeItemFactory.create()


@pytest.fixture
def classquiz_params(school_class: SchoolClass,
                     knowledge_item_: KnowledgeItem,
                     subject_: Subject) -> Dict:  # noqa
    questions = QuestionsFactory.create_batch(5,
                                              subject_id=subject_.id,
                                              multiple_choice_question_type=True,
                                              with_choices={
                                                  'knowledge_item': knowledge_item_
                                              })
    dumper = QuestionsSchema()
    questions = [dumper.dump(question) for question in questions]

    return build(dict, FACTORY_CLASS=ClassQuizFactory, class_id=school_class.id, questions=questions)  # noqa


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


@pytest.fixture
def quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, score=None)


@pytest.fixture
def breakdown() -> List[List[Dict]]:
    return [
        [
            {
                'insert': "Argon only makes up 1% of Earth's atmosphere.\nEarth's \
                    atmosphere is composed of 78% nitrogen, 21% oxygen, 1% argon and 0.04% carbon dioxide.\n"  # noqa
            }
        ],
        [
            {
                'insert': "You mixed up Oxygen and Nitrogen.\nEarth's \
                    atmosphere is composed of 78% nitrogen, 21% oxygen, 1% argon and 0.04% carbon dioxide.\n"  # noqa
            },
            {
                'attributes': {
                    'background': '#f5f5f5',
                    'link': 'https://earthhow.com/wp-content/uploads/2018/10/Atmosphere-Composition.png'  # noqa
                },
                'insert': 'Image'
            },
            {
                'insert': '\n'
            }
        ],
        [
            {
                'insert': "Carbon Dioxide only makes a TINY part of the atmosphere (0.04%).\nNitrogen (78%) is the most abundant gas in Earth's atmosphere.\n"  # noqa
            }
        ],
        [
            {
                'insert': "You may have mixed up Argon with Carbon Dioxide.\nCarbon Dioxide only makes up 0.04% of Earth's atmosphere.\n"  # noqa
            }
        ],
        [
            {
                'insert': '\n'
            }
        ]
    ]


def dummy_jwt_identity() -> Dict:
    return {
        'identity': {
            'email': 'dummy@example.com'
        }
    }


def mock_jwt_required() -> bool:
    return True


def test_classquiz_create_api(client: FlaskClient,
                              classquiz_params: Dict,
                              mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    response = client.post(
        "/api/v1/class_quiz",
        json=classquiz_params,
    )

    assert response.status_code == 201
    cq = ClassQuiz.query.first()

    assert cq.url is not None


def test_classquiz_create_api_with_no_question_fails(client: FlaskClient,
                                                     classquiz_params: Dict,
                                                     mocker: MockFixture):
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    classquiz_params.pop('questions')
    response = client.post(
        "/api/v1/class_quiz",
        json=classquiz_params,
    )

    assert response.status_code == 400


def test_classquiz_get_api(client: FlaskClient,
                           classquiz_: ClassQuiz):

    response = client.get(f'/api/v1/class_quiz/{classquiz_.uuid}')

    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert data['data']['subject'] in ['Chemistry', 'Biology', 'Physics']


def test_classquiz_report_card_fetch_api(client: FlaskClient,
                                         quiz_grade: QuizGrade,
                                         mocker: MockFixture,
                                         breakdown: List[List[Dict]]) -> None:  # noqa
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    # update with gradebreakdown
    quiz_grade.update_grade_breakdown(breakdown)

    response = client.get(f"/api/v1/class_quiz/report_card/{quiz_grade.uuid}")

    assert response.status_code == 200


def test_classquiz_report_card_fetch_api_id_validation(client: FlaskClient,
                                                       quiz_grade: QuizGrade,
                                                       mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    from uuid import uuid4
    response = client.get(f"/api/v1/class_quiz/report_card/{str(uuid4()).replace('-', '')}")
    assert response.status_code == 400


def test_classquiz_report_card_fetch_api_errors_if_not_found(client: FlaskClient,
                                                             quiz_grade: QuizGrade,
                                                             mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_quiz_generation_email')
    mocker.patch('server.api.class_quiz_api.get_jwt_identity', dummy_jwt_identity)

    from uuid import uuid4
    response = client.get(f"/api/v1/class_quiz/report_card/{uuid4()}")
    assert response.status_code == 404


def test_classquiz_send_report_card(client: FlaskClient,
                                    quiz_grade: QuizGrade,
                                    mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_report_card_pdf')

    response = client.get(f"/api/v1/class_quiz/{quiz_grade.uuid}/send_report")
    assert response.status_code == 200


def test_classquiz_send_report_card_grade_not_found(client: FlaskClient,
                                                    mocker: MockFixture) -> None:
    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_report_card_pdf')

    response = client.get(f"/api/v1/class_quiz/{uuid4()}/send_report")
    assert response.status_code == 404


def test_classquiz_send_report_card_exception(client: FlaskClient,
                                              quiz_grade: QuizGrade,
                                              mocker: MockFixture) -> None:

    def _mock_send_report_card_pdf(*args):
        raise Exception()

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.api.class_quiz_api.send_report_card_pdf', _mock_send_report_card_pdf)

    response = client.get(f"/api/v1/class_quiz/{quiz_grade.uuid}/send_report")
    assert response.status_code == 500


def test_classquiz_get_graded_quizzes(client: FlaskClient,
                                      quiz_grade: QuizGrade,
                                      classquiz_: ClassQuiz,
                                      mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.get(f"/api/v1/class_quiz/{classquiz_.uuid}/graded")
    assert response.status_code == 200
