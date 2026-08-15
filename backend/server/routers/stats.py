"""FastAPI port of ``server/api/stats_api.py``."""

from fastapi import APIRouter, Depends

from server.auth import with_required_roles
from server.routers.helpers import json_response

stats_router = APIRouter(tags=["stats"])


@stats_router.get("/stats/ping")
def stats_ping():
    return json_response(
        {"status": "success", "message": "Pinged the stats api"}
    )


@stats_router.get("/stats/correct_response")
def stats_correct_response(_: object = Depends(with_required_roles(["Admin", "Teacher"]))):
    """Returns a list of labels and results grouped by question.

    Not implemented upstream (the legacy endpoint body was ``pass``); kept as
    a role-guarded placeholder returning an empty document.
    """
    return json_response({})
