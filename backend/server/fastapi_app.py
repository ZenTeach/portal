"""FastAPI application factory for the Zenteach portal backend.

This module is the new ASGI entry point for the backend. It reuses the
existing ORM layer unchanged by providing:

* ``server.db`` -- a plain-SQLAlchemy compatibility singleton (see
  :mod:`server.db`) that mirrors the Flask-SQLAlchemy surface the models use.
* ``server.security.bcrypt`` -- a Flask-free password hashing facade.
* a plain ``redis`` client for the token blocklist store.
* a fake :class:`flask.Flask` app that hosts configuration and keeps
  Flask-Migrate (``flask db`` CLI) working against the same models.

Routes are added progressively as the Flask blueprints are ported.
"""

import os

from fastapi import FastAPI
from flask import Flask
from flask_migrate import Migrate
from sqlalchemy_searchable import make_searchable
from starlette.middleware.cors import CORSMiddleware

import server
import redis as redis_lib
from server.config.settings import get_settings
from server.db import db
from server.security import bcrypt  # noqa: F401  (kept for parity)

__all__ = ["create_fastapi_app"]


def _build_flask_compat_app():
    """Create the fake Flask app used for config + Flask-Migrate compat."""
    flask_app = Flask(__name__)

    settings = get_settings()
    flask_app.config.update(settings.flask_config())
    flask_app.config.update(
        database_url=settings.database_url or ""
    )

    return flask_app


def _cors_origins():
    origins = get_settings().allowed_cors_origin or "*"
    if origins == "*":
        return ["*"]
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def _install_redis_store():
    """Expose a plain redis client as ``server.redis_store``.

    Auth APIs import ``from server import redis_store`` to set/read JWT jti
    blocklist keys. The legacy app uses FlaskRedis (bound to ``REDIS_URL`` at
    init); the FastAPI app installs an equivalent plain client keyed off the
    same environment variable.
    """
    url = get_settings().redis_url
    client = redis_lib.Redis.from_url(url, decode_responses=True)
    server.redis_store = client
    return client


def create_fastapi_app() -> FastAPI:
    """Build and return the FastAPI application."""
    flask_app = _build_flask_compat_app()

    # ORM layer -- shared compatibility singleton (no Flask app required).
    db.init_app(flask_app)
    make_searchable(db.metadata, options={"regconfig": "pg_catalog.simple"})

    # Redis blocklist store.
    _install_redis_store()

    # Import models so they register on ``db.metadata`` (and Flask-Migrate
    # sees the full schema).
    import server.models  # noqa: F401

    # Flask-Migrate compat for the ``flask db`` CLI + Alembic env.py.
    Migrate(flask_app, db, directory=os.path.join("server", "models", "migrations"))

    fastapi_app = FastAPI(
        title="Zenteach Portal API",
        version="2.0.0",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS -- mirrors the Flask extension config.
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=60 * 60 * 24,
    )

    @fastapi_app.get("/healthcheck")
    def healthcheck():
        return {"status": "success", "message": "Pinged the fastapi healthcheck"}

    return fastapi_app


app = create_fastapi_app()
"""Module-level ASGI app for uvicorn/gunicorn."""


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server.fastapi_app:app", host="0.0.0.0", port=5000)
