#!/usr/bin/env python
import os

from celery.schedules import crontab
from server import celery, create_app  # noqa
from server.config import CeleryConfig
from server.tasks import (check_all_quizzes_administered,
                          check_all_quizzes_graded,
                          grade_all_administered_quizzes)

# update celery config
celery.conf.update(**CeleryConfig()._asdict())


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(minute='*/3'),
        check_all_quizzes_administered.s(),
        name='checking all administered quizzes')

    # Grade quizzes
    sender.add_periodic_task(
        crontab(minute='*/10'),
        grade_all_administered_quizzes.s(),
        name='Grading all submitted quizzes'
    )

    sender.add_periodic_task(
        crontab(minute='*/15'),
        check_all_quizzes_graded.s(),
        name='checking all graded quizzes')

    # Monthly summarizer
    # sender.add_periodic_task(
    #     crontab(day_of_month='1'),
    #     enqueue_summary_for_teacher.s(),
    #     name='Enqueue summary for teacher: monthly')

    # Weekly summarizer
    # sender.add_periodic_task(
    #     crontab(day_of_week='', month_of_year='*'),
    #     enqueue_summary_for_teacher.s(),
    #     name='Enqueue summary for teacher: weekly')

    # Daily summarizer
    # sender.add_periodic_task(
    #     crontab(hour='22', minute='1', day_of_week='*'),
    #     enqueue_summary_for_teacher.s(),
    #     name='Enqueue summary for teacher: daily')


sentry_dsn_key = os.environ.get("SENTRY_DSN")
if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(dsn=sentry_dsn_key, integrations=[CeleryIntegration(), RedisIntegration()])

app = create_app()
app.app_context().push()
