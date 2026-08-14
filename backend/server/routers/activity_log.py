"""FastAPI port of ``server/api/activity_log_api.py``."""

from fastapi import APIRouter, Depends

from server.auth import jwt_required
from server.models import ActivityLogSchema, Teacher
from server.routers.helpers import json_response

activity_log_router = APIRouter(tags=["activity-log"])

schema_dumper = ActivityLogSchema()


@activity_log_router.get("/activity_logs")
def activity_logs(teacher: Teacher = Depends(jwt_required(fresh=True))):
    activity_logs_ = teacher.activity_logs.limit(10)
    return json_response(schema_dumper.dump(activity_logs_, many=True))
