import datetime
import os
from logging import CRITICAL, getLogger
from pathlib import Path
from shutil import which
from typing import List, Tuple

import pytest
from flask.testing import FlaskClient
from server import create_app, db
from server.models import Teacher
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy_searchable import sync_trigger

getLogger('factory').setLevel(CRITICAL)
getLogger('factory.generate').setLevel(CRITICAL)
getLogger('faker.factory').setLevel(CRITICAL)


@pytest.fixture(scope="session")
def engine():
    return create_engine(os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="session")
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
        sync_search_vector_triggers(db.engine, [
            ('questions', 'question'),
            ('topics', 'value'),
            ('knowledge_items', 'value')
        ])
        yield app.test_client()
        db.session.remove()  # looks like db.session.close() would work as well
        db.drop_all()
        db.engine.dispose()


def sync_search_vector_triggers(engine: Engine, table_search_entity_list: List[Tuple[str, str]]):
    for table_search_entity in table_search_entity_list:
        sync_trigger(engine, table_search_entity[0], "search_vector", [table_search_entity[1]])


@pytest.fixture(scope="function")
def teacher_identity(client: FlaskClient) -> Teacher:
    from server.tests.factories import TeacherFactory
    with client.session_transaction():
        teacher = TeacherFactory.create()
    return teacher


@pytest.fixture(autouse=True)
def access_token(client: FlaskClient, teacher_identity: Teacher) -> List[str]:
    from datetime import timedelta

    from flask_jwt_extended import (create_access_token, create_refresh_token,
                                    get_csrf_token, get_jti)
    from server import redis_store
    from server.lib.utils.jwt_fixes import (set_access_cookies,
                                            set_refresh_cookies)

    access_token = create_access_token(teacher_identity.id, fresh=True)
    refresh_token = create_refresh_token(teacher_identity.id)
    set_access_cookies(client, access_token, legacy=True)

    set_refresh_cookies(client, refresh_token, legacy=True)
    access_jti = get_jti(access_token)
    refresh_jti = get_jti(refresh_token)
    redis_store.set(access_jti, "true", timedelta(minutes=30) * 1.2)
    redis_store.set(refresh_jti, "true", timedelta(minutes=30) * 1.2)

    return [access_token,
            refresh_token,
            get_csrf_token(access_token),
            get_csrf_token(refresh_token)]


@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'eventlet'


@pytest.fixture
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
def file_fixture_dir() -> str:
    return Path.joinpath(Path(__file__).parent, 'fixtures/files').as_posix()


def chrome_like_binary() -> str:
    chromium_binary = which('chromium')
    if chromium_binary is None:
        chromium_binary = which('google-chrome')

    return chromium_binary


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.binary_location = f"{chrome_like_binary()}"
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    return chrome_options


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    timestamp = datetime.datetime.now().strftime('%H-%M-%S')
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call':
        feature_request = item.funcargs['request']
        screenshot_dir = make_screenshot_dir()
        markers = [marker.name for marker in item.own_markers]
        if 'e2e' not in markers:
            return
        driver = feature_request.getfixturevalue('selenium')

        # always add url to report
        xfail = hasattr(report, 'wasxfail')
        if (report.skipped and xfail) or (report.failed and not xfail):
            # only add additional html on failure
            driver.save_screenshot(f"{screenshot_dir}/screenshot-{timestamp}.png")


def make_screenshot_dir() -> str:
    path = Path(f"{os.getcwd()}/tmp/selenium")  # nosec
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

    return str(path)
