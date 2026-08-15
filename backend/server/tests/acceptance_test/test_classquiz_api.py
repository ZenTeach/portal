import json
from typing import Dict, List, Union
from uuid import UUID, uuid4

import pytest
from factory import build
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.models import (ClassQuiz, KnowledgeItem, QuestionsSchema,
                           QuizGrade, QuizSession, SchoolClass, Student,
                           Subject, Teacher, Topic)
from server.tests.factories import (ClassQuizFactory, KnowledgeItemFactory,
                                    QuestionsFactory, QuizGradeFactory,
                                    QuizSessionFactory, SchoolClassFactory,
                                    StudentFactory, SubjectFactory,
                                    TopicFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def subject_() -> Subject:
    return SubjectFactory(name="Chemistry")


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def anon_student(school_class: SchoolClass) -> Student:
    return Student.create_anonymous_student(classes=[school_class], confirmed=True)


@pytest.fixture
def topic_(subject_: Subject) -> Topic:
    return TopicFactory(subject_id=subject_.id)


@pytest.fixture
def knowledge_item_(topic_: Topic, subject_: Subject) -> KnowledgeItem:
    return KnowledgeItemFactory(topic_id=topic_.id, subject_id=subject_.id)


@pytest.fixture
def classquiz_params(school_class: SchoolClass,
                     knowledge_item_: KnowledgeItem,
                     topic_: Topic,
                     subject_: Subject) -> Dict:  # noqa
    questions = []
    for _ in range(5):
        questions.append(
            QuestionsFactory(subject_id=subject_.id,
                             multiple_choice_question_type=True,
                             knowledge_item=knowledge_item_,
                             topic=topic_)
        )
    questions = QuestionsSchema.dump_many(questions)

    return build(dict, FACTORY_CLASS=ClassQuizFactory, class_id=school_class.id, questions=questions)  # noqa


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id, private=True)
    cq.save(refresh=True)

    return cq


@pytest.fixture
def quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, score=None)


@pytest.fixture
def quiz_grade_uuid(quiz_grade: QuizGrade) -> UUID:
    return quiz_grade.uuid


@pytest.fixture
def anon_student_graded_session(anon_student: Student, classquiz_: ClassQuiz) -> QuizSession:
    session = QuizSessionFactory(student_id=anon_student.id,
                                 class_quiz_id=classquiz_.id)
    grade = QuizGradeFactory(uuid=uuid4(), student_id=anon_student.id,  # noqa
                             class_quiz_id=classquiz_.id, graded=True, score=None)

    return session


@pytest.fixture
def anon_student_session_uuid(anon_student_graded_session: QuizSession) -> UUID:
    return anon_student_graded_session.uuid


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
                              access_token: List[str],
                              mocker: MockFixture):
    def patch_log_activity(*args):
        assert len(args) == 6

    mocker.patch('server.routers.class_quiz.log_activity', patch_log_activity)

    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')
    response = client.post(
        "/api/v1/class_quiz",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        },
        json=classquiz_params,
    )

    assert response.status_code == 201
    cq = ClassQuiz.query.first()

    assert cq.url is not None
    assert cq.name is not None


def test_classquiz_create_api_with_no_question_fails(client: FlaskClient,
                                                     classquiz_params: Dict,
                                                     teacher_identity: Teacher,
                                                     access_token: List[str],
                                                     mocker: MockFixture):
    def patch_log_activity(*args):
        assert len(args) == 6

    mocker.patch('server.routers.class_quiz.log_activity', patch_log_activity)
    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')

    classquiz_params.pop('questions')
    response = client.post(
        "/api/v1/class_quiz",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        },
        json=classquiz_params,
    )

    assert response.status_code == 400


def test_classquiz_create_api_with_nonexisting_question_fails(client: FlaskClient,
                                                              classquiz_params: Dict,
                                                              teacher_identity: Teacher,
                                                              access_token: List[str],
                                                              mocker: MockFixture):
    def patch_log_activity(*args):
        assert len(args) == 6

    mocker.patch('server.routers.class_quiz.log_activity', patch_log_activity)
    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')

    questions = classquiz_params.pop('questions')
    questions[1]['id'] = 0
    classquiz_params['questions'] = questions
    response = client.post(
        "/api/v1/class_quiz",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        },
        json=classquiz_params,
    )

    assert response.status_code == 400


def test_classquiz_get_api(client: FlaskClient,
                           access_token: List[str],
                           classquiz_: ClassQuiz):

    response = client.get(
        f'/api/v1/class_quiz/{classquiz_.uuid}',
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200
    data = json.loads(response.content.decode())
    assert data['data']['subject'] in ['Chemistry', 'Biology', 'Physics']


def test_classquiz_update_api(client: FlaskClient,
                              access_token: List[str],
                              mocker: MockFixture,
                              classquiz_params: dict,
                              classquiz_: ClassQuiz):
    def patch_log_activity(*args):
        assert len(args) == 6

    mocker.patch('server.routers.class_quiz.log_activity', patch_log_activity)
    old_name = classquiz_.name
    assert classquiz_.private
    classquiz_params = {
        'name': "A new quiz name",
        'private': False
    }
    response = client.patch(
        f'/api/v1/class_quiz/{classquiz_.uuid}',
        json=classquiz_params,
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })

    assert response.status_code == 200
    classquiz_.reload()
    assert not classquiz_.private
    assert old_name != classquiz_.name


@pytest.mark.parametrize(
    "logged_in,report_card,status_code",
    [
        pytest.param(
            True, 'quiz_grade_uuid', 200
        ),
        pytest.param(
            False, 'quiz_grade_uuid', 401
        ),
        pytest.param(
            False, 'anon_student_session_uuid', 200
        )
    ]
)
def test_classquiz_report_card_fetch_api(client: FlaskClient,
                                         quiz_grade: QuizGrade,
                                         mocker: MockFixture,
                                         logged_in: bool,
                                         report_card: Union[int, UUID],
                                         status_code: int,
                                         access_token: List[str],
                                         request,
                                         breakdown: List[List[Dict]]) -> None:  # noqa
    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')

    report_card_or_session_uuid = request.getfixturevalue(report_card)
    # update with gradebreakdown
    # quiz_grade.update_grade_breakdown(breakdown)
    response = None

    if logged_in:
        response = client.get(
            f"/api/v1/class_quiz/report_card/{report_card_or_session_uuid}",
            headers={
                'Authorization': 'Bearer {}'.format(access_token[0]),
                'X-CSRF-ACCESS-TOKEN': access_token[2]
            })
    else:
        response = client.get(
            f"/api/v1/class_quiz/report_card/{report_card_or_session_uuid}")

    assert response.status_code == 200


def test_classquiz_report_card_fetch_api_id_validation(client: FlaskClient,
                                                       quiz_grade: QuizGrade,
                                                       access_token: List[str],
                                                       teacher_identity: Teacher,
                                                       mocker: MockFixture) -> None:

    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')

    from uuid import uuid4
    response = client.get(
        f"/api/v1/class_quiz/report_card/{str(uuid4()).replace('-', '')}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 400


def test_classquiz_report_card_fetch_api_errors_if_not_found(client: FlaskClient,
                                                             quiz_grade: QuizGrade,
                                                             access_token: List[str],
                                                             teacher_identity: Teacher,
                                                             mocker: MockFixture) -> None:

    mocker.patch('server.routers.class_quiz.send_quiz_generation_email')

    from uuid import uuid4
    response = client.get(
        f"/api/v1/class_quiz/report_card/{uuid4()}",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 404


def test_classquiz_send_report_card(client: FlaskClient,
                                    quiz_grade: QuizGrade,
                                    access_token: List[str],
                                    mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.routers.class_quiz.send_report_card_pdf')

    response = client.get(
        f"/api/v1/class_quiz/{quiz_grade.uuid}/send_report",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200


def test_classquiz_send_report_card_grade_not_found(client: FlaskClient,
                                                    teacher_identity: dict,
                                                    access_token: List[str],
                                                    mocker: MockFixture) -> None:

    mocker.patch('server.routers.class_quiz.send_report_card_pdf')

    response = client.get(
        f"/api/v1/class_quiz/{uuid4()}/send_report",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 404


def test_classquiz_send_report_card_exception(client: FlaskClient,
                                              quiz_grade: QuizGrade,
                                              access_token: List[str],
                                              mocker: MockFixture) -> None:

    def _mock_send_report_card_pdf(*args):
        raise Exception()

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")
    mocker.patch('server.routers.class_quiz.send_report_card_pdf', _mock_send_report_card_pdf)

    response = client.get(
        f"/api/v1/class_quiz/{quiz_grade.uuid}/send_report",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 500


def test_classquiz_get_graded_quizzes(client: FlaskClient,
                                      quiz_grade: QuizGrade,
                                      access_token: List[str],
                                      classquiz_: ClassQuiz,
                                      mocker: MockFixture) -> None:

    mocker.patch("flask_jwt_extended.view_decorators.verify_jwt_in_request")

    response = client.get(
        f"/api/v1/class_quiz/{classquiz_.uuid}/graded",
        headers={
            'Authorization': 'Bearer {}'.format(access_token[0]),
            'X-CSRF-ACCESS-TOKEN': access_token[2]
        })
    assert response.status_code == 200
