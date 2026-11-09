"""FastAPI port of ``server/api/knowledge_item_api.py``."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends

from server.auth import jwt_required
from server.models import KnowledgeItemSchema, Subject, Teacher, Topic
from server.models.knowledge_item import KnowledgeItem
from server.routers.helpers import error_response, json_response, logger

knowledge_item_router = APIRouter(tags=["knowledge-items"])


@knowledge_item_router.get("/knowledge_items")
def knowledge_items_list(_: Teacher = Depends(jwt_required(fresh=True))):
    return json_response({"data": KnowledgeItemSchema.dump_many(KnowledgeItem.query.all())})


@knowledge_item_router.post("/knowledge_items")
def knowledge_items_create(
    ki_data: Optional[Dict[str, Any]] = Body(None),
    teacher: Teacher = Depends(jwt_required(fresh=True)),
):
    if not ki_data:
        return error_response("", 400)

    subject_ = Subject.query.filter_by(name=ki_data.pop("subject")).first()
    topic = Topic.query.filter_by(value=ki_data.pop("topic")).first()

    if not subject_:
        return error_response("", 404)
    if not topic:
        return error_response("", 404)

    ki_data.update(
        {"teacher_id": teacher.id, "subject_id": subject_.id, "topic_id": topic.id}
    )

    ki = KnowledgeItem(**ki_data)
    try:
        ki.save()
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("", 500)

    return json_response({"data": KnowledgeItemSchema.dump_one(ki)}, 201)


@knowledge_item_router.get("/knowledge_item/{knowledge_item_id}")
def knowledge_item_get(
    knowledge_item_id: int, _: Teacher = Depends(jwt_required(fresh=True))
):
    knowledge_item = KnowledgeItem.query.filter_by(id=knowledge_item_id).first()
    if not knowledge_item:
        return json_response(
            {"data": [], "message": "Topic content not found."}, 404
        )
    return json_response({"data": KnowledgeItemSchema.dump_one(knowledge_item)})


@knowledge_item_router.put("/knowledge_item/{knowledge_item_id}")
def knowledge_item_update(
    knowledge_item_id: int,
    ki_data: Optional[Dict[str, Any]] = Body(None),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    knowledge_item: KnowledgeItem = KnowledgeItem.query.filter_by(
        id=knowledge_item_id
    ).first()
    if not knowledge_item:
        return json_response(
            {"data": [], "message": "Topic content not found."}, 404
        )
    if not ki_data:
        return error_response("", 400)

    try:
        knowledge_item.update_and_save(**ki_data)
        knowledge_item.save()
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("", 500)

    return json_response({"data": KnowledgeItemSchema.dump_one(knowledge_item)})


@knowledge_item_router.post("/knowledge_item/search")
def knowledge_item_search(
    payload: Optional[Dict[str, Any]] = Body(None),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    payload = payload or {}
    search = payload.get("search")
    subject_name = payload.get("subject")
    topic_value = payload.get("topic")

    subject = Subject.query.filter_by(name=subject_name).first()
    topic = Topic.query.filter_by(value=topic_value).first()

    if not search:
        return error_response("", 400)
    if not topic:
        return error_response("", 400)

    knowledge_items = KnowledgeItem.query.search(search)

    if subject:
        knowledge_items = knowledge_items.filter_by(subject_id=subject.id)
    if topic:
        knowledge_items = knowledge_items.filter_by(topic_id=topic.id)

    knowledge_items = knowledge_items.all()

    return json_response({"data": KnowledgeItemSchema.dump_many(knowledge_items)})
