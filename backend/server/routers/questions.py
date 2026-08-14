"""FastAPI port of ``server/api/questions_api.py``."""

from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, Response
from pydantic import ValidationError
from sqlalchemy import exc

from server import db
from server.auth import jwt_required, with_required_roles
from server.lib import format_pydantic_validation_for_api
from server.models import (
    KnowledgeItem,
    Questions,
    QuestionsSchema,
    Subject,
    Teacher,
    Topic,
)
from server.models.question_choice import QuestionChoice
from server.models.questions import AdminFormValidator as QuestionSchemaValidator
from server.routers.helpers import error_response, json_response, log_activity, logger

question_router = APIRouter(tags=["questions"])


@question_router.get("/question")
def question_list_get(subject: str, _: Teacher = Depends(jwt_required(fresh=True))):
    question_list = None
    if subject == "":
        question_list = []
    else:
        subject_ = Subject.query.filter(Subject.name.op("~*")(subject)).first()
        if subject_ is None:
            return json_response(
                {
                    "questions": [],
                    "message": f"{subject} subject not found",
                },
                400,
            )
        question_list = Questions.query.filter_by(subject_id=subject_.id).all()

    return json_response(
        {
            "questions": QuestionsSchema.dump_many(question_list)
        }
    )


@question_router.post("/question")
def question_list_post(_: Teacher = Depends(jwt_required(fresh=True)), data: Dict[str, Any] = Body(None)):
    error_object = {"status": "fail", "message": "Invalid payload."}

    if not data:
        return json_response(error_object, 400)

    try:
        question_entry = Questions.query.filter_by(
            subject_id=data.get("subject_id"),
            tag=data.get("tag"),
            question=data.get("question"),
        ).first()
        if not question_entry:
            Questions.create_from_admin_form(data)
            return json_response(
                {"status": "success", "message": "Question was added!"}, 201
            )
        else:
            return json_response(
                {"status": "fail", "message": "Question already exists."}, 400
            )
    except ValidationError as e:
        logger.error(e)
        return json_response(error_object, 400)
    except Exception as e:  # noqa: BLE001
        db.session.rollback()
        logger.error(e)
        return json_response(error_object, 500)


@question_router.post("/question/search")
def question_search(
    query_params: Dict[str, Any] = Body(...),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    try:
        subject_ = Subject.query.filter(Subject.name == query_params["subject"]).first()
        if subject_ is None:
            return error_response("Subject not found", 404)

        if query_params["query"] == "":
            return error_response("Query cannot be empty", 400)
        if query_params["query"] == "*":
            result_set = Questions.query.filter_by(subject_id=subject_.id)
        else:
            result_set = Questions.query.search(
                query_params["query"]
            ).filter_by(subject_id=subject_.id)

        if len(query_params["topic"]) != 0:
            result_set = result_set.join(Topic).filter(
                Topic.value.in_(query_params["topic"])
            )

        if len(query_params["knowledge_item"]) != 0:
            result_set = result_set.join(KnowledgeItem).filter(
                KnowledgeItem.value.in_(query_params["knowledge_item"])
            )

        result_set = result_set.all()

        logger.debug(f"Result set length: {len(result_set)}")
        if len(result_set) != 0:
            return json_response(
                {"data": QuestionsSchema.dump_many(result_set)}
            )
        else:
            return json_response({"message": "No result found"})
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("Error processing request", 500)


@question_router.post("/question/filter/ki")
def question_ki_filter(
    data: Dict[str, Any] = Body(...),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    topics_selected = data.get("topics_selected")

    if topics_selected is None:
        return json_response("Please select topics first.", 400)

    if len(topics_selected) == 0:
        return json_response("", 404)

    try:
        filtered_kis = KnowledgeItem.query.join(Topic).filter(
            Topic.value.in_(topics_selected)
        ).all()
        for_response = [(ki.topic.value, ki.value) for ki in filtered_kis]

        return json_response(for_response)
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("Error filtering Topic contents", 500)


@question_router.get("/question/filter/topic/{subject}")
def question_topic_filter(
    subject: str, _: Teacher = Depends(jwt_required(fresh=True))
):
    try:
        subject_ = Subject.query.filter(Subject.name.op("~*")(subject)).first()
        if subject_ is None:
            return json_response({}, 400)
        topics = (
            Topic.query.filter(Topic.subject_id == subject_.id)
            .filter(Topic.value.isnot(None))
            .filter(Topic.value != "")
            .distinct(Topic.value)
            .all()
        )

        response = [topic.value for topic in topics]
        return json_response(response)
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("Error filtering topics", 500)


@question_router.post("/question/fetch")
def question_from_kis_and_topics(
    json_payload: Dict[str, Any] = Body(...),
    _: Teacher = Depends(jwt_required(fresh=True)),
):
    topics = json_payload.get("topics", [])
    kis = json_payload.get("kis", [])
    query = Questions.query

    if len(topics) == 0 and len(kis) == 0:
        return error_response("Topic and Topic contents not set", 400)

    if len(topics) != 0:
        query = query.join(Topic).filter(Topic.value.in_(topics))
    if len(kis) != 0:
        selected_kis_id = [
            k.id
            for k in KnowledgeItem.query.filter(
                KnowledgeItem.value.in_(kis)
            ).all()
        ]
        query = query.filter(Questions.knowledge_item_id.in_(selected_kis_id))

    questions = query.all()
    return json_response({"data": QuestionsSchema.dump_many(questions)})


@question_router.get("/question/user_created")
def teacher_owned_questions(teacher: Teacher = Depends(jwt_required(fresh=True))):
    questions = teacher.questions
    return json_response(
        {"questions": QuestionsSchema.dump_many(questions)}
    )


@question_router.post("/question/user_created")
def teacher_owned_questions_create(
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    data: Dict[str, Any] = Body(None),
):
    data = data or {}
    data.update({"user_created": True})

    try:
        QuestionSchemaValidator.model_validate(data)
    except ValidationError as exc:
        errors = format_pydantic_validation_for_api(exc)
        return json_response(errors, 422)

    if teacher.id != data.get("teacher_id", None):
        return error_response("Teacher is not recognized", 422)

    if "subject" in data:
        subject_id = Subject.query.filter_by(name=data.pop("subject")).first().id
        data.update(subject_id=subject_id)
    if "knowledge_item" in data:
        knowledge_item = KnowledgeItem.query.filter_by(
            value=data.pop("knowledge_item")
        ).first()
        data.update({"knowledge_item": knowledge_item})

    if "topic" in data:
        topic = Topic.query.filter_by(value=data.pop("topic")).first()
        data.update({"topic": topic})

    choices = data.pop("choices")
    for choice in choices:
        choice.update({"user_created": True, "teacher_id": teacher.id})
    data.update({"choices": choices})

    question = Questions(**data)
    try:
        question.save()
        log_activity(
            teacher,
            "create",
            "question",
            question.id,
            {},
            f"{teacher.full_name()} created question {question.id}",
        )
        return json_response({"message": "Question successfully added"}, 201)
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        return json_response(
            {
                "message": "Run into an error creating question. We will take a look in a bit!"
            },
            500,
        )


@question_router.delete("/question/user_created/{question_id}")
def teacher_owned_question_delete(
    question_id: int, teacher: Teacher = Depends(jwt_required(fresh=True))
):
    question: Questions = Questions.query.filter_by(id=question_id).first()

    if question is None:
        return error_response("Question doesn't exist.", 404)

    if question.teacher_id != teacher.id:
        return error_response(
            "The selected question doesn't belong to the teacher", 422
        )

    try:
        question_id = question.id
        question.delete()
        log_activity(
            teacher,
            "delete",
            "question",
            question.id,
            {},
            f"{teacher.full_name()} deleted question {question_id}",
        )
        return json_response({"message": "Question deleted successfully!"}, 204)
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        return error_response("We ran into a problem deleting the question.", 500)


@question_router.patch("/question/user_created/{question_id}")
def teacher_owned_question_update(
    question_id: int,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    data: Dict[str, Any] = Body(None),
):
    success_message = {"message": "Question was updated successfully."}
    status_code = 200
    question: Questions = Questions.query.filter_by(id=question_id).first()

    if question is None:
        return error_response("Question doesn't exist.", 404)

    if data is None:
        return error_response("Cannot update question with empty values.", 400)

    try:
        if "subject" in data:
            subject_id = Subject.query.filter_by(name=data.pop("subject")).first().id
            data.update(subject_id=subject_id)

        if "knowledge_item" in data:
            knowledge_item = (
                KnowledgeItem.query.filter_by(value=data.pop("knowledge_item"))
                .first()
            )
            data.update(
                {
                    "knowledge_item": knowledge_item,
                    "knowledge_item_id": knowledge_item.id,
                }
            )

        if "topic" in data:
            topic = Topic.query.filter_by(value=data.pop("topic")).first()
            data.update({"topic": topic, "topic_id": topic.id})

        if question.teacher_id != teacher.id:
            question = Questions.empty_instance()
            data.update({"user_created": True})
            success_message["message"] = "Question successfully added."
            status_code = 201

        if "choices" in data:
            choices = data.pop("choices")
            choice_objects = []
            correct_choice_uuid = [
                choice["uuid"]
                for choice in choices
                if choice["is_correct_choice"]
            ][0]

            for choice_data in choices:
                c = QuestionChoice.query.filter_by(
                    uuid=choice_data.pop("uuid")
                ).first()
                choice = None
                is_cloned_choice_correct = False
                if c is not None:
                    # We clone the choices when it's created freshly by a user
                    if not c.user_created:
                        choice = QuestionChoice.clone(
                            c,
                            autosave=True,
                            **{
                                "user_created": True,
                                "teacher_id": teacher.id,
                            },
                        )
                        if str(c.uuid) == correct_choice_uuid:
                            is_cloned_choice_correct = True
                    else:
                        choice = c
                        choice.update_and_save(**choice_data)
                        choice.save()

                    choice_objects.append(choice)
                    if str(choice.uuid) == correct_choice_uuid or is_cloned_choice_correct:
                        data.update({"correct_choice_id": choice.id})
                else:
                    new_choice = QuestionChoice(
                        **choice_data,
                        user_created=True,
                        teacher_id=teacher.id,
                    )
                    new_choice.save()
                    choice_objects.append(new_choice)
                    if choice_data.get("is_correct_choice"):
                        data.update({"correct_choice_id": new_choice.id})

            data.update({"choices": choice_objects})

        question.update_and_save(**data)
        question.save()
        log_activity(
            teacher,
            "update",
            "question",
            question.id,
            {},
            f"{teacher.full_name()} updated question {question.id}",
        )

        return json_response(success_message, status_code)
    except Exception as e:  # noqa: BLE001
        logger.exception(e)
        return error_response("We ran into a problem updating the question.", 500)


@question_router.get("/question/{question_id}")
def question_get(
    question_id: int, _: Teacher = Depends(jwt_required(fresh=True))
):
    question = Questions.query.filter_by(id=question_id).first()
    return json_response({"question": QuestionsSchema.dump_one(question)})


@question_router.delete("/question/{question_id}")
def question_delete(
    question_id: int, _: Teacher = Depends(jwt_required(fresh=True))
):
    try:
        question = Questions.query.filter_by(id=question_id).first()
        if not question:
            return error_response("Question not found", 400)
        db.session.delete(question)
        return json_response(
            {"message": "Deleted question {}".format(question.id)}, 204
        )
    except exc.IntegrityError as e:
        logger.error(e)
        db.session.rollback()
        return error_response(
            "Error while deleteing \
                        question id: {}".format(
                question_id
            ),
            500,
        )


@question_router.put("/question/{question_id}")
def question_put(
    question_id: int, _: object = Depends(with_required_roles(["Admin"]))
):
    """Not implemented upstream (legacy body was ``pass``)."""
    return json_response({})
