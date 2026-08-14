"""Shared helpers for the FastAPI routers.

Provides Flask-free stand-ins for the utilities the legacy blueprints imported
from ``server.api``:

* ``logger`` — a plain stdlib logger (no Flask ``current_app``).
* ``log_activity`` — wraps :meth:`server.models.ActivityLog.log` behind the
  ``LOG_ACTIVITY`` setting (read from the pydantic settings instead of Flask's
  ``current_app.config``).
* ``redis_store`` — accessor for the plain redis client installed on
  ``server.redis_store`` by :func:`server.fastapi_app._install_redis_store`.
"""

import logging
from typing import Any, Optional

from fastapi.responses import JSONResponse

import server
from server.config.settings import get_settings
from server.models import ActivityLog

logger = logging.getLogger("zenteach.fastapi")


def json_response(content: Any, status_code: int = 200) -> JSONResponse:
    """Return a JSONResponse with the given content and status code."""
    return JSONResponse(content=content, status_code=status_code)


def error_response(message: str, status_code: int) -> JSONResponse:
    """Return a JSON error response with a ``message`` key."""
    return json_response({"message": message}, status_code)


def redis_store():
    """Return the shared redis blocklist client (installed at app creation)."""
    return server.redis_store


def log_activity(
    user,
    action: str,
    item_type: str,
    item_id: int,
    attributes: Optional[dict] = None,
    note: Optional[str] = None,
) -> None:
    """Record an :class:`ActivityLog` row when ``LOG_ACTIVITY`` is enabled."""
    if not get_settings().log_activity:
        return
    ActivityLog.log(user, action, item_type, item_id, attributes or {}, note)
