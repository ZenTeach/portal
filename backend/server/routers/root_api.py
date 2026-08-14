"""FastAPI port of the ``root`` blueprint from ``server/api/__init__.py``.

Exposes the unauthenticated ``/subjects`` and ``/settings`` endpoints under
``/api/v1`` exactly as the legacy blueprint did.
"""

from fastapi import APIRouter

from server.models import Setting, SettingSchema, Subject, SubjectSchema
from server.routers.helpers import json_response

root_api_router = APIRouter(tags=["root"])


@root_api_router.get("/subjects")
def subjects():
    subjects_ = Subject.query.all()
    return json_response({"subjects": SubjectSchema.dump_many(subjects_)})


@root_api_router.get("/settings")
def settings():
    return json_response(SettingSchema.dump_one(Setting()))
