"""FastAPI port of ``server/api/class_quiz_api.py``."""

import re
from typing import Dict, Union
from uuid import UUID

from fastapi import APIRouter, Body, Depends
from marshmallow import INCLUDE, Schema, ValidationError, fields, validates_schema
from sqlalchemy import exc

from server import db
from server.auth import jwt_required, with_required_roles
from server.models import ClassQuiz as ClassQuizModel
from server.models import (
    ClassQuizSchema,
    ClassQuizStatus,
    Questions,
    QuizGrade,
    QuizGradeSchema,
    QuizSession,
    StudentSchema,
    Teacher,
)
from server.tasks import send_quiz_generation_email, send_report_card_pdf
from server.routers.helpers import error_response, json_response, log_activity, logger

class_quiz_router = APIRouter(tags=["class-quiz"])

dumper = ClassQuizSchema()
students_dumper = StudentSchema(many=True)


class ClassQuizCreateQuestionChoicesSchema(Schema):
    class Meta:
        unknown = INCLUDE

    uuid = fields.Str(required=True)
    value = fields.Str(required=True)


class ClassQuizCreateTopicSchema(Schema):
    class Meta:
        unknown = INCLUDE

    value = fields.Str(required=True)


class ClassQuizCreateKnowledgeItemSchema(Schema):
    class Meta:
        unknown = INCLUDE

    value = fields.Str(required=True)


class ClassQuizCreateQuestionsSchema(Schema):
    class Meta:
        unknown = INCLUDE

    knowledge_item = fields.Nested(
        ClassQuizCreateKnowledgeItemSchema, required=True, unknown=INCLUDE
    )
    question_type = fields.Int(required=True)
    choices = fields.Nested(
        ClassQuizCreateQuestionChoicesSchema, many=True, required=True
    )
    topic = fields.Nested(ClassQuizCreateTopicSchema, required=True)
    subject = fields.Dict(keys=fields.Str, values=fields.Str, required=True)
    tag = fields.Str(required=True)
    question = fields.Str(required=True)
    id = fields.Int(required=True)


class ClassQuizCreateSchema(Schema):
    class Meta:
        unknown = INCLUDE

    subject = fields.Str(required=True)
    name = fields.Str(required=True)
    class_id = fields.Int(required=True)
    questions = fields.Nested(ClassQuizCreateQuestionsSchema, many=True, required=True)

    @validates_schema(pass_original=True)
    def validate_selected_questions(self, *values, **kwargs):
        data = values[0]
        question_ids = [question["id"] for question in data["questions"]]
        questions = Questions.query.filter(Questions.id.in_(question_ids))
        if questions.count() != len(question_ids):
            raise ValidationError(
                "Invalid question found! Please report this so we can fix it!"
            )


class ClassQuizUpdateSchema(Schema):
    class Meta:
        unknown = INCLUDE

    name = fields.Str(required=True)
    private = fields.Boolean(required=False)


@class_quiz_router.get("/class_quiz")
def class_quiz_list(_: object = Depends(with_required_roles(["Teacher", "Admin"]))):
    return json_response(
        {
            "status": "success",
            "data": {
                "class_quizzes": [
                    dumper.dump(classquiz)
                    for classquiz in ClassQuizModel.query.all()
                ]
            },
        }
    )


@class_quiz_router.post("/class_quiz")
def class_quiz_create(
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    post_data: Dict = Body(None),
):
    teacher_email = teacher.email
    error_object = {"status": "Failed", "message": "Quiz data not given."}
    if not post_data:
        return json_response(error_object, 400)

    validation_errors = None
    try:
        validation_errors = ClassQuizCreateSchema().validate(data=post_data)

        if validation_errors is not None and len(validation_errors) != 0:
            raise ValidationError("Malformed data")

        quiz = ClassQuizModel(**post_data)
        quiz.save()
        log_activity(
            teacher,
            "create",
            "class_quiz",
            quiz.id,
            {},
            f"{teacher} created a quiz for class {quiz.class_id}",
        )
        response_object = {"status": "success", "message": "Quiz was added!"}
        send_quiz_generation_email.apply_async(args=[teacher_email, quiz.id])
        return json_response(response_object, 201)
    except ValidationError:
        return json_response(
            {"status": "failed", "message": validation_errors}, 400
        )
    except exc.IntegrityError as e:
        db.session.rollback()
        logger.error(e)
        return json_response(
            {"status": "failed", "message": "Quiz couldn't be created!"}, 500
        )


@class_quiz_router.get("/class_quiz/report_card/{uuid}")
def class_quiz_report_card(uuid: str):
    # Validate the UUID string
    validator = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$"
    )
    if validator.match(uuid) is None:
        return error_response("Report Card id given is unknown or malformed", 400)

    hyphen_count = uuid.count("-")
    if hyphen_count > 0:
        uuid = uuid.replace("-", "")
    total_score = ""
    grade = QuizGrade.query.filter_by(uuid=uuid).first()
    if not grade:
        session = QuizSession.query.filter_by(uuid=uuid).first()
        if not session:
            return error_response("Student or quiz don't exist.", 404)
        else:
            student = session.student
            grade = QuizGrade.query.filter_by(
                class_quiz_id=session.class_quiz_id
            ).filter_by(student_id=student.id).first()
    total_score = f"{grade.score}/{grade.class_quiz.max_score}"
    return json_response(
        {"report_card": grade.grade_breakdown, "score": total_score}
    )


@class_quiz_router.get("/class_quiz/{class_quiz_uuid}/attended_students")
def class_quiz_attended_students(
    class_quiz_uuid: str, _: Teacher = Depends(jwt_required(fresh=True))
):
    quiz = ClassQuizModel.query.filter_by(
        uuid=class_quiz_uuid, status=ClassQuizStatus.administered
    ).first()
    if len(quiz.student_quiz_grades) == 0:
        return error_response("Student or quiz don't exist.", 404)

    students = quiz.student_quiz_grades
    responses = students_dumper.dump(students)

    return json_response(responses)


@class_quiz_router.get("/class_quiz/{quiz_uuid}/graded")
def class_quiz_graded(
    quiz_uuid: str, _: Teacher = Depends(jwt_required(fresh=True))
):
    quizId = ClassQuizModel.query.filter_by(uuid=quiz_uuid).first().id
    graded_quizzes = QuizGrade.query.filter_by(
        class_quiz_id=quizId, graded=True
    ).all()

    serializer = QuizGradeSchema(many=True)
    return json_response(serializer.dump(graded_quizzes))


@class_quiz_router.get("/class_quiz/{quiz_grade_uuid}/send_report")
def class_quiz_send_report_card(
    quiz_grade_uuid: UUID, _: Teacher = Depends(jwt_required(fresh=True))
):
    grade = QuizGrade.query.filter_by(uuid=quiz_grade_uuid).first()

    if not grade:
        return error_response("Report card not found!", 404)

    try:
        send_report_card_pdf.apply_async(args=[grade.uuid])
    except Exception:  # noqa: BLE001
        return error_response(
            "Server run into an error sending report card. We're working to resolve the issue",
            500,
        )
    else:
        return json_response(
            {
                "status": "success",
                "message": "Report card email has been sent!",
            }
        )


@class_quiz_router.get("/class_quiz/{class_quiz_uuid}")
def class_quiz_get(class_quiz_uuid: str):
    error_response_ = {"message": "No Class Quiz found."}
    try:
        class_quiz = ClassQuizModel.query.filter_by(uuid=class_quiz_uuid).first()
        if not class_quiz:
            return json_response(error_response_, 404)
        else:
            return json_response(
                {
                    "status": "success",
                    "data": dumper.dump(class_quiz),
                }
            )
    except ValueError:
        return json_response(error_response_, 404)


@class_quiz_router.delete("/class_quiz/{class_quiz_id}")
def class_quiz_delete(
    class_quiz_id: str,
    teacher: Teacher = Depends(with_required_roles(["Teacher", "Admin"])),
):
    error_response_ = {"message": "No Class Quiz found."}
    try:
        class_quiz = ClassQuizModel.query.filter_by(id=class_quiz_id).first()
        if not class_quiz:
            return json_response(error_response_, 404)
        else:
            class_quiz_id = class_quiz.id
            class_quiz.delete()
            log_activity(
                teacher,
                "delete",
                "class_quiz",
                class_quiz_id,
                {},
                "Deleted Class Quiz.",
            )
            response_message = {"status": "success", "message": "Deleted Quiz"}
            return json_response(response_message)
    except exc.DatabaseError as e:  # noqa
        return json_response(error_response_, 404)


@class_quiz_router.patch("/class_quiz/{class_quiz_uuid}")
def class_quiz_update(
    class_quiz_uuid: str,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    post_data: Dict = Body(None),
):
    error_object = {"status": "Failed", "message": "Quiz data not given."}
    if not post_data:
        return json_response(error_object, 400)

    validation_errors = None
    class_quiz: ClassQuizModel = ClassQuizModel.query.filter_by(
        uuid=class_quiz_uuid
    ).first()
    try:
        validation_errors = ClassQuizUpdateSchema().validate(data=post_data)
        if validation_errors is not None and len(validation_errors) != 0:
            raise ValidationError("Malformed data")
        class_quiz.update_and_save(**post_data, refresh=True)
        log_activity(
            teacher,
            "update",
            "class_quiz",
            class_quiz.id,
            {},
            "Updated Class Quiz.",
        )
        return json_response(
            {"status": "updated", "message": "Quiz updated"}
        )
    except ValidationError:
        return json_response(
            {"status": "failed", "message": validation_errors}, 400
        )
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return json_response(
            {"status": "failed", "message": "Quiz couldn't be updated!"}, 500
        )
