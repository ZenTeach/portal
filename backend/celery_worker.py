#!/usr/bin/env python
import os

from server import celery, create_app  # noqa

# from server.tasks import grader_administered_quizzes
# from celery.schedules import crontab

# NOTE: not needed at this moment
# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(
#        crontab(minute='*/15'),
#        grader_administered_quizzes.s(),
#        name='grade quizzes')

sentry_dsn_key = os.environ.get("SENTRY_DSN")
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(dsn=sentry_dsn_key, integrations=[CeleryIntegration(), RedisIntegration()])

app = create_app()
app.app_context().push()
