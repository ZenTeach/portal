"""FastAPI port of ``server/api/topic_api.py``."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends

from server.auth import jwt_required
from server.models import Subject, Teacher, Topic, TopicSchema
from server.routers.helpers import error_response, json_response, logger

topic_router = APIRouter(tags=["topics"])


@topic_router.get("/topics")
def topics_list(_: Teacher = Depends(jwt_required(fresh=True))):
    dumper = TopicSchema(many=True)
    return json_response({"data": dumper.dump(Topic.query.all())})


@topic_router.post("/topics")
def topics_create(
    topic_data: Optional[Dict[str, Any]] = Body(None),
    teacher: Teacher = Depends(jwt_required(fresh=True)),
):
    if not topic_data:
        return error_response("", 400)

    subject_ = Subject.query.filter_by(name=topic_data.pop("subject")).first()
    if not subject_:
        return error_response("", 404)

    topic_data.update({"teacher_id": teacher.id, "subject_id": subject_.id})

    dumper = TopicSchema()
    topic = Topic(**topic_data)
    try:
        topic.save()
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("", 500)

    return json_response({"data": dumper.dump(topic)}, 201)


@topic_router.get("/topic/{topic_id}")
def topic_get(topic_id: int, _: Teacher = Depends(jwt_required(fresh=True))):
    dumper = TopicSchema()
    topic = Topic.query.filter_by(id=topic_id).first()
    if not topic:
        return json_response({"data": [], "message": "Topic not found."}, 404)
    return json_response({"data": dumper.dump(topic)})


@topic_router.put("/topic/{topic_id}")
def topic_update(
    topic_id: int,
    topic_data: Optional[Dict[str, Any]] = Body(None),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    topic: Topic = Topic.query.filter_by(id=topic_id).first()
    if not topic:
        return json_response({"data": [], "message": "Topic not found."}, 404)
    if not topic_data:
        return error_response("", 400)

    dumper = TopicSchema()
    try:
        topic.update_and_save(**topic_data)
        topic.save()
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("", 500)

    return json_response({"data": dumper.dump(topic)})


@topic_router.post("/topics/search")
def topics_search(
    payload: Optional[Dict[str, Any]] = Body(None),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    payload = payload or {}
    search = payload.get("search")
    subject_name = payload.get("subject")
    subject = Subject.query.filter_by(name=subject_name).first()

    if not search:
        return error_response("", 400)

    dumper = TopicSchema(many=True)
    topics = Topic.query.search(search)
    if subject:
        topics = topics.filter_by(subject_id=subject.id)
    topics = topics.all()

    return json_response({"data": dumper.dump(topics)})
