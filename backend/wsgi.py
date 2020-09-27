import os

from aiohttp import web
from aiohttp_wsgi import WSGIHandler
from server import create_app

sentry_dsn_key = os.environ.get("SENTRY_DSN")
app = None

if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=sentry_dsn_key,
        integrations=[
            FlaskIntegration(),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
    )


def make_aiohttp_app():
    app = create_app()
    wsgi_handler = WSGIHandler(app)
    aioapp = web.Application()
    aioapp.router.add_route("*", "/{path_info:.*}", wsgi_handler)
    return aioapp


app = make_aiohttp_app()
