"""FastAPI routers — the ported equivalents of the Flask blueprints.

Each module here mirrors one (or more) legacy modules under ``server/api``.
Routers are registered on the FastAPI app in :mod:`server.fastapi_app` with the
same ``/api/v1`` prefix the blueprints used.
"""

from server.routers.activity_log import activity_log_router
from server.routers.class_quiz import class_quiz_router
from server.routers.knowledge_item import knowledge_item_router
from server.routers.questions import question_router
from server.routers.quiz_submit import quiz_submit_router
from server.routers.root_api import root_api_router
from server.routers.school_class import school_class_router
from server.routers.stats import stats_router
from server.routers.student_auth import student_auth_router
from server.routers.teacher_auth import teacher_auth_router
from server.routers.topic import topic_router

__all__ = [
    "activity_log_router",
    "class_quiz_router",
    "knowledge_item_router",
    "question_router",
    "quiz_submit_router",
    "root_api_router",
    "school_class_router",
    "stats_router",
    "teacher_auth_router",
    "student_auth_router",
    "topic_router",
]
