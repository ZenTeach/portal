import datetime
import os
from logging import CRITICAL, getLogger
from pathlib import Path
from shutil import which
from typing import List, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy_searchable import sync_trigger

from server import db
from server.auth import (
    create_access_token,
    create_refresh_token,
    get_csrf_token,
    get_jti,
)
from server.auth.cookies import (
    ACCESS_COOKIE_NAME,
    ACCESS_CSRF_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    REFRESH_CSRF_COOKIE_NAME,
)
from server.fastapi_app import create_fastapi_app
from server.models import Teacher

getLogger('factory').setLevel(CRITICAL)
getLogger('factory.generate').setLevel(CRITICAL)
getLogger('faker.factory').setLevel(CRITICAL)


def _test_database_url() -> str:
    url = os.environ.get("DATABASE_TEST_URL")
    if not url:
        raise RuntimeError("DATABASE_TEST_URL must be set to run the test suite")
    return url


@pytest.fixture(scope="session")
def engine():
    return create_engine(_test_database_url())


@pytest.fixture(scope="session")
def app():
    # Point the shared DB singleton at the test database. The explicit URI
    # takes precedence over the URL baked into the Flask compat config, so the
    # FastAPI app (and everything under it) talks to the test DB.
    db.init_app(uri=_test_database_url())
    return create_fastapi_app()


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium


@pytest.fixture(scope="function")
def client(app):
    from server.db import _request_session_scope
    db.init_app(uri=_test_database_url())
    db.create_all()
    sync_search_vector_triggers(db.engine, [
        ('questions', 'question'),
        ('topics', 'value'),
        ('knowledge_items', 'value')
    ])
    # Pre-bind a single request scope spanning the whole test so the pytest
    # thread (factories/fixtures) and the TestClient worker thread (request
    # handlers) share one SQLAlchemy session. This avoids the cross-session
    # deadlocks and staleness that occur when each side holds its own
    # transaction on the same rows.
    scope = "test"
    token = _request_session_scope.set(scope)
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        db.session.remove()
        _request_session_scope.reset(token)
        db.drop_all()
        db.engine.dispose()


def sync_search_vector_triggers(engine: Engine, table_search_entity_list: List[Tuple[str, str]]):
    for table_search_entity in table_search_entity_list:
        sync_trigger(engine, table_search_entity[0], "search_vector", [table_search_entity[1]])


@pytest.fixture(scope="function")
def teacher_identity(client: TestClient) -> Teacher:
    from server.tests.factories import TeacherFactory
    return TeacherFactory.create()


@pytest.fixture(autouse=True)
def access_token(client: TestClient, teacher_identity: Teacher) -> List[str]:
    import server

    access_token = create_access_token(
        teacher_identity.id, fresh=True, user_type="teacher"
    )
    refresh_token = create_refresh_token(teacher_identity.id, user_type="teacher")

    # Prime the client cookie jar with the same cookies the SPA would receive
    # from a real login, so FastAPI's cookie-based token resolution works.
    client.cookies.set(ACCESS_COOKIE_NAME, access_token)
    client.cookies.set(REFRESH_COOKIE_NAME, refresh_token)
    client.cookies.set(ACCESS_CSRF_COOKIE_NAME, get_csrf_token(access_token))
    client.cookies.set(REFRESH_CSRF_COOKIE_NAME, get_csrf_token(refresh_token))

    # Default double-submit CSRF header for the access token, so requests that
    # don't pass headers explicitly still satisfy the CSRF check (mirrors the
    # legacy tests, where `verify_jwt_in_request` was mocked to a no-op and the
    # cookies alone authenticated every request).
    client.headers["X-CSRF-ACCESS-TOKEN"] = get_csrf_token(access_token)

    # Allowlist the jtis so the (allowlist-semantics) blocklist check passes.
    store = getattr(server, "redis_store", None)
    if store is not None:
        store.set(get_jti(access_token), "true")
        store.set(get_jti(refresh_token), "true")

    return [
        access_token,
        refresh_token,
        get_csrf_token(access_token),
        get_csrf_token(refresh_token),
    ]


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
