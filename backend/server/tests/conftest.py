import datetime
import os
from contextlib import nullcontext
from logging import CRITICAL, getLogger
from pathlib import Path
from shutil import which

import pytest
from server import create_app
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_searchable import sync_trigger

getLogger('factory').setLevel(CRITICAL)
getLogger('factory.generate').setLevel(CRITICAL)


@pytest.fixture(scope="session")
def engine():
    return create_engine(os.environ.get("DATABASE_TEST_URL"))


@pytest.fixture(scope="session")
def app():
    _app = create_app()
    _app.config.from_object("server.config.TestingConfig")
    _appctx = nullcontext(_app)
    with _appctx as app:
        app.app_context().push()
        yield app
        app.app_context().pop()


@pytest.fixture(scope="function")
@pytest.mark.usefixtures('app')
def db(app):
    db_connection = app.extensions['sqlalchemy'].db
    connection = db_connection.engine.connect()
    transaction = connection.begin()
    db_connection.create_all()
    sync_trigger(connection, "questions", "search_vector", ["question"])
    session = db_connection.session
    yield session
    db_connection.session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def selenium(selenium):
    selenium.implicitly_wait(10)
    selenium.maximize_window()
    return selenium


@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'solo'


@pytest.fixture(scope="function")
@pytest.mark.usefixtures('app')
@pytest.mark.usefixtures('db')
def client(app, db):
    with app.test_client() as client:
        yield client


@pytest.fixture(scope='session')
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
