import os
from logging import CRITICAL, getLogger
from pathlib import Path

import pytest
from pytest_factoryboy import register
from server import create_app, db
from server.tests.factories import (ClassQuizFactory, QuestionChoiceFactory,
                                    QuizGradeFactory, QuizSessionFactory,
                                    SchoolClassFactory, StudentFactory,
                                    TeacherFactory)
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

register(ClassQuizFactory, "class_quiz")
register(SchoolClassFactory, "school_class")
register(TeacherFactory, "teacher")
register(QuizGradeFactory, "quiz_grade")
register(QuizSessionFactory, "quiz_session")
register(StudentFactory, "student")
register(QuestionChoiceFactory)

getLogger('factory').setLevel(CRITICAL)


@pytest.fixture(scope="session")
def engine():
    return create_engine(os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium


@pytest.fixture(scope="function")
def client():
    app = create_app()
    app.config.from_object("server.config.TestingConfig")
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()  # looks like db.session.close() would work as well
        db.drop_all()


@pytest.yield_fixture
def dbsession(engine):
    """Returns an sqlalchemy session, and after the test
        tears down everything properly."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(autouse=True)
def after_each_cleanup(mocker):
    mocker.resetall()


@pytest.fixture(autouse=True)
def file_fixture_dir():
    return Path.joinpath(Path(__file__).parent, 'fixtures/files').as_posix()


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.binary_location = '/usr/bin/google-chrome'
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    return chrome_options
