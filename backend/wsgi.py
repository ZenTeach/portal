import logging
import os

from aiohttp import web
from aiohttp_wsgi import WSGIHandler
from prometheus_flask_exporter.multiprocess import GunicornPrometheusMetrics
from server import create_app

sentry_dsn_key = os.environ.get("SENTRY_DSN")
app = None


if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.aiohttp import AioHttpIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=sentry_dsn_key,
        traces_sample_rate=0.7,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
            AioHttpIntegration(),
            sentry_logging
        ],
    )


def when_ready(server):
    if os.environ.get('RUNTIME') == 'production':
        GunicornPrometheusMetrics.start_http_server_when_ready(8000)


def child_exit(server, worker):
    GunicornPrometheusMetrics.mark_process_dead_on_child_exit(worker.pid)


def make_aiohttp_app():
    app = create_app()
    wsgi_handler = WSGIHandler(app)
    aioapp = web.Application()
    aioapp.router.add_route("*", "/{path_info:.*}", wsgi_handler)
    return aioapp


app = make_aiohttp_app()
