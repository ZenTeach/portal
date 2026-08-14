"""FastAPI routers — the ported equivalents of the Flask blueprints.

Each module here mirrors one (or more) legacy modules under ``server/api``.
Routers are registered on the FastAPI app in :mod:`server.fastapi_app` with the
same ``/api/v1`` prefix the blueprints used.
"""

from server.routers.student_auth import student_auth_router
from server.routers.teacher_auth import teacher_auth_router

__all__ = ["teacher_auth_router", "student_auth_router"]
