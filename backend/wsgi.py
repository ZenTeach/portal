"""ASGI entry point for gunicorn (uvicorn worker).

The legacy module bridged the Flask WSGI app through aiohttp-WSGI. The backend
now exposes a native ASGI app (``server.fastapi_app:app``), so gunicorn runs it
directly with ``uvicorn.workers.UvicornWorker`` (see ``entrypoint.sh``).

Sentry is initialized here with ASGI/FastAPI integrations instead of the old
Flask + aiohttp integrations, and the app is wrapped in ``SentryAsgiMiddleware``.
"""

import logging
import os

from server.fastapi_app import app  # noqa: F401  (ASGI app for gunicorn)

sentry_dsn_key = os.environ.get("SENTRY_DSN")

if sentry_dsn_key:
    import sentry_sdk
    from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
    from sentry_sdk.integrations.starlette import StarletteIntegration

    sentry_logging = LoggingIntegration(
        level=logging.INFO,        # Capture info and above as breadcrumbs
        event_level=logging.ERROR  # Send errors as events
    )

    sentry_sdk.init(
        dsn=sentry_dsn_key,
        traces_sample_rate=0.7,
        integrations=[
            StarletteIntegration(transaction_style="url"),
            FastApiIntegration(transaction_style="url"),
            SqlalchemyIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
            sentry_logging,
        ],
    )

    app = SentryAsgiMiddleware(app)
