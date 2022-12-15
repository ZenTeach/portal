import pytest
from flask.testing import FlaskClient
from pytest import fail
from pytest_mock import MockFixture
from server.lib.grader import Grader
from server.models import (QuizGrade, QuizSession, QuizSessionStatus,
                           SchoolClass, Student, Teacher)
from server.models.class_quiz import ClassQuiz, ClassQuizStatus
from server.tasks.grader_tasks import (check_all_quizzes_administered,
                                       check_all_quizzes_graded,
                                       grade_all_quizzes, grade_quiz,
                                       regrade_quiz)
from server.tests.factories import (ClassQuizFactory, QuizGradeFactory,
                                    SchoolClassFactory, StudentFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(with_classquiz=True, teacher_id=teacher_.id)


@pytest.fixture
def student_(client: FlaskClient, school_class) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def classquiz(client: FlaskClient, school_class: SchoolClass) -> ClassQuiz:
    return school_class.quizzes[0]


@pytest.fixture
def administered_classquiz(client: FlaskClient,
                           student_: Student,
                           school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.create(class_id=school_class.id, with_multiple_choice_questions=4)
    QuizSession(student_id=student_.id,
                class_quiz_id=cq.id,
                status=QuizSessionStatus.ended).save()
    return cq


@pytest.fixture
def ended_quiz_session(client: FlaskClient,
                       student_: Student,
                       classquiz: ClassQuiz) -> QuizSession:

    session = QuizSession(student_id=student_.id,
                          class_quiz_id=classquiz.id,
                          status=QuizSessionStatus.ended)
    session.save()
    return session


@pytest.fixture
def graded_classquiz(client: FlaskClient,
                     student_: Student,
                     school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.create(class_id=school_class.id, with_multiple_choice_questions=4)
    QuizSession(student_id=student_.id,
                class_quiz_id=cq.id,
                status=QuizSessionStatus.ended).save()

    QuizGradeFactory(student_id=student_.id,
                     class_quiz_id=cq.id, graded=True)
    return cq


@pytest.fixture
def quiz_grade_(client: FlaskClient, student_: Student, classquiz: ClassQuiz):
    QuizSession(student_id=student_.id,
                class_quiz_id=classquiz.id,
                status=QuizSessionStatus.ended).save()

    return QuizGradeFactory(student_id=student_.id,
                            class_quiz_id=classquiz.id)


def test_check_all_quizzes_administered(client: FlaskClient,
                                        mocker: MockFixture,
                                        administered_classquiz: ClassQuiz):
    assert ClassQuiz.query.filter_by(status=ClassQuizStatus.administered).count() == 0
    check_all_quizzes_administered()
    assert ClassQuiz.query.filter_by(status=ClassQuizStatus.administered).count() == 1


def test_check_all_quizzes_graded(client: FlaskClient,
                                  mocker: MockFixture,
                                  graded_classquiz: ClassQuiz):
    # Case 2: ClassQuiz graded
    assert ClassQuiz.query.filter_by(status=ClassQuizStatus.graded).count() == 0
    check_all_quizzes_graded()
    assert ClassQuiz.query.filter_by(status=ClassQuizStatus.graded).count() == 1


def test_grade_quiz_runs(client: FlaskClient, monkeypatch):
    def mock_from_quiz_session(x):
        return True
    monkeypatch.setattr(Grader, 'from_quiz_session', mock_from_quiz_session)
    try:
        grade_quiz('some_foo_id')
    except Exception as exception:
        raise fail("DID RAISE {0}".format(exception))


def test_grader_regrade_quiz(client: FlaskClient,
                             mocker: MockFixture,
                             student_: Student,
                             quiz_grade_: QuizGrade,
                             classquiz: ClassQuiz):
    mocker.patch('server.tasks.grader_tasks.grade_quiz')

    @mocker.patch('server.models.QuizGrade.prepare_regrade_')
    def mocked_quiz_grade_method(prepare_regrade_mock):
        prepare_regrade_mock.assert_called()

    @mocker.patch('server.tasks.grader_tasks.regrade_quiz')
    def mocked_grader_tasks(regrade_quiz_mock):
        regrade_quiz_mock.assert_called_with(classquiz.id, student_.id)

    regrade_quiz(classquiz.id, student_.id)


def test_grade_all_quizzes(client: FlaskClient,
                           mocker: MockFixture,
                           ended_quiz_session: QuizSession):
    mocked_grade_quiz = mocker.patch('server.tasks.grader_tasks.grade_quiz.apply_async')
    grade_all_quizzes()
    mocked_grade_quiz.assert_called_with(args=[ended_quiz_session.uuid])
