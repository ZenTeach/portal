from server import create_app, db
import pytest
import os
import pytest_mock
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import mock
from pytest_factoryboy import register, LazyFixture
from server.tests.factories import StudentFactory, TeacherFactory, SchoolClassFactory, ClassQuizFactory, QuizGradeFactory, QuizSessionFactory, QuestionsFactory, QuestionChoiceFactory

register(ClassQuizFactory, "class_quiz")
register(SchoolClassFactory, "school_class")
register(TeacherFactory, "teacher")
register(QuizGradeFactory, "quiz_grade")
register(QuizSessionFactory, "quiz_session")
register(StudentFactory, "student")
register(QuestionsFactory, "questions")
register(QuestionChoiceFactory)
@pytest.fixture(scope="session")
def engine():
    return create_engine(os.environ.get('DATABASE_TEST_URL'))


@pytest.fixture(scope="function")
def client():
    app = create_app()
    app.config.from_object('server.config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()  # looks like db.session.close() would work as well
        db.drop_all()


@pytest.yield_fixture
def dbsession(engine):
    """Returns an sqlalchemy session, and after the test tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(autouse=True)
def after_each_cleanup(mocker):
    # import pdb; pdb.set_trace()
    mocker.resetall()
