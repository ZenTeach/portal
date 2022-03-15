#!/usr/bin/env python
import os

from celery.schedules import crontab
from server import celery, create_app  # noqa
from server.tasks import (check_all_quizzes_administered,
                          check_all_quizzes_graded)


# NOTE: not needed at this moment
@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/3'),
        check_all_quizzes_administered.s(),
        name='checking all administered quizzes')
    sender.add_periodic_task(
        crontab(minute='*/15'),
        check_all_quizzes_graded.s(),
        name='checking all graded quizzes')


sentry_dsn_key = os.environ.get("SENTRY_DSN")
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(dsn=sentry_dsn_key, integrations=[CeleryIntegration(), RedisIntegration()])

app = create_app()
app.app_context().push()
