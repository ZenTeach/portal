#!/usr/bin/env python
import logging
import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv
from server.config import CeleryConfig
from server.config.settings import get_settings
from server.tasks import (check_all_quizzes_administered,
                          check_all_quizzes_graded, grade_all_quizzes,
                          send_graded_quizzes)

if os.getenv('RUNTIME') == 'development':
    load_dotenv()

celery = Celery("zenteach_tasks")
TaskBase = celery.Task

celery.conf.update(**CeleryConfig()._asdict())


def _create_task_app():
    """Build a minimal Flask app carrying only what background tasks need.

    Tasks use ``db`` (the plain-SQLAlchemy scoped session), ``mail``
    (Flask-Mail) and ``render_template`` (Jinja). Those require a Flask app
    with the settings loaded and those extensions initialized -- but not
    Flask-Admin, JWT, CORS or the API blueprints -- so we build a bare app
    instead of ``create_app()``.
    """
    from flask import Flask
    from sqlalchemy_searchable import make_searchable

    from server import mail, redis_store
    from server.db import db

    flask_app = Flask(__name__, template_folder="templates")
    flask_app.config.update(get_settings().flask_config())

    db.init_app(flask_app)
    make_searchable(db.metadata, options={"regconfig": "pg_catalog.simple"})
    mail.init_app(flask_app)
    redis_store.init_app(flask_app)

    # Register models on db.metadata so task imports resolve the full schema.
    import server.models  # noqa: F401
    return flask_app


app = _create_task_app()


class ContextTask(TaskBase):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            try:
                return TaskBase.__call__(self, *args, **kwargs)
            finally:
                # Release the thread-local scoped session so connections are
                # returned to the pool between tasks (no Flask app context
                # teardown does this for us anymore).
                from server.db import db
                db.session.remove()


celery.Task = ContextTask


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/3'),
        check_all_quizzes_administered.s(),
        name='checking all administered quizzes')

    # Grade quizzes
    sender.add_periodic_task(
        crontab(minute='*/1'),
        grade_all_quizzes.s(),
        name='Grading all submitted quizzes'
    )

    sender.add_periodic_task(
        crontab(minute='*/15'),
        check_all_quizzes_graded.s(),
        name='checking all graded quizzes')

    sender.add_periodic_task(
        crontab(minute='*/2'),
        send_graded_quizzes.s(),
        name="Send all graded report cards"
    )


sentry_dsn_key = os.environ.get("SENTRY_DSN")
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=sentry_dsn_key,
        traces_sample_rate=1.0,
        integrations=[
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
            sentry_logging
        ],
    )
