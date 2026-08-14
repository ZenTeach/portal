"""FastAPI port of ``server/api/school_class_api.py``."""

from typing import Any, Dict

from fastapi import APIRouter, Body, Depends
from marshmallow import INCLUDE, Schema, fields
from sqlalchemy import exc

from server import db
from server.auth import jwt_required, with_required_roles
from server.models import SchoolClass as SchoolClassModel
from server.models import SchoolClassSchema, Student, Subject, Teacher
from server.tasks import send_student_confirmation_instructions
from server.routers.helpers import error_response, json_response, log_activity, logger

school_class_router = APIRouter(tags=["school-classes"])

schema_dumper = SchoolClassSchema()


class PatchPayloadSchema(Schema):
    class Meta:
        unknown = INCLUDE

    new_email = fields.Email(required=True)
    old_email = fields.Email(required=True)


@school_class_router.get("/school_class/owned")
def teacher_owned_class(teacher: Teacher = Depends(jwt_required(fresh=True))):
    error_object = {"message": ""}
    try:
        classrooms = SchoolClassModel.query.filter_by(
            teacher_id=int(teacher.id)
        )

        if not classrooms:
            error_object["message"] = "No class rooms found"
            return json_response(error_object)
        else:
            return json_response(
                {
                    "status": "success",
                    "data": [schema_dumper.dump(c) for c in classrooms],
                }
            )
    except Exception as e:  # noqa: BLE001
        logger.debug(e)
        error_object["message"] = "Error processing request"
        return json_response(error_object, 500)


@school_class_router.get("/school_class/owned/{teacher_id}")
def school_class_owned(
    teacher_id: int, _: object = Depends(with_required_roles(["Admin"]))
):
    error_message = {"message": "Class room doesn't exist"}
    try:
        classrooms = SchoolClassModel.query.filter_by(
            teacher_id=int(teacher_id)
        ).all()
        if not classrooms:
            return json_response(error_message, 404)
        else:
            return json_response(
                {
                    "status": "success",
                    "data": [schema_dumper.dump(c) for c in classrooms],
                }
            )
    except ValueError:
        return json_response(error_message, 400)


@school_class_router.get("/school_class")
def school_class_list(_: Teacher = Depends(jwt_required(fresh=True))):
    return json_response(
        {
            "status": "success",
            "data": {
                "school_classes": [
                    schema_dumper.dump(classroom)
                    for classroom in SchoolClassModel.query.all()
                ]
            },
        }
    )


@school_class_router.post("/school_class")
def school_class_create(
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    post_data: Dict[str, Any] = Body(None),
):
    error_object = {"status": "fail", "message": "Invalid payload."}
    if not post_data:
        return json_response(error_object, 400)

    name = post_data.get("name")
    subject = post_data.get("subject")
    start_date = post_data.get("start_date")
    exam_board = post_data.get("exam_board")
    year_group = post_data.get("year_group")
    teacher_id = teacher.id
    subject = Subject.query.filter_by(name=subject).first()
    if not subject:
        return error_response("Subject not recognized or has been disabled.", 400)

    try:
        school_class = SchoolClassModel.query.filter_by(name=name).first()
        if not school_class:
            school_class = SchoolClassModel(
                name=name,
                subject_id=subject.id,
                exam_board=exam_board,
                start_date=start_date,
                teacher_id=teacher_id,
                year_group=year_group,
            )
            school_class.save()
            log_activity(
                teacher,
                "create",
                "student_class",
                school_class.id,
                {},
                "",
            )
            return json_response(
                {"status": "success", "message": "{} was added!".format(name)},
                201,
            )
        else:
            return json_response(
                {"status": "fail", "message": "School class already exists."}, 400
            )
    except exc.IntegrityError as err:  # noqa
        db.session.rollback()
        return json_response(error_object, 500)


@school_class_router.get("/school_class/{school_class_id}")
def school_class_get(
    school_class_id: int, _: Teacher = Depends(jwt_required(fresh=True))
):
    error_response_ = {"message": "Class room doesn't exist"}
    try:
        class_room = SchoolClassModel.query.filter_by(
            id=school_class_id
        ).first()
        if not class_room:
            return json_response(error_response_, 404)
        else:
            return json_response(
                {
                    "status": "success",
                    "data": schema_dumper.dump(class_room),
                }
            )
    except ValueError:
        return json_response(error_response_, 404)


@school_class_router.delete("/school_class/{school_class_id}")
def school_class_delete(
    school_class_id: int, teacher: Teacher = Depends(jwt_required(fresh=True))
):
    try:
        class_room = SchoolClassModel.query.filter_by(id=school_class_id).first()

        if not class_room:
            return json_response(
                {"status": "failure", "message": "Classroom not found"}, 404
            )

        SchoolClassModel.remove_classroom(class_room)
        log_activity(
            teacher,
            "delete",
            "school_class",
            class_room.id,
            {},
            f"Removed class {class_room.name}",
        )
        return json_response(
            {
                "status": "success",
                "message": "Classroom was successfully deleted.",
            },
            204,
        )
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return json_response(
            {
                "status": "success",
                "message": "Encountered an error while deleting classroom.",
            },
            500,
        )


@school_class_router.put("/school_class/{school_class_id}")
def school_class_update(
    school_class_id: int,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    update_data: Dict[str, Any] = Body(None),
):
    update_data = update_data or {}

    subject = None
    if update_data.get("subject") is not None:
        subject = Subject.query.filter(
            Subject.name == update_data.pop("subject")
        ).first()

    error_response_ = {"message": "Class room doesn't exist"}
    class_room = SchoolClassModel.query.filter_by(id=school_class_id).first()

    if not class_room:
        return json_response(error_response_, 404)

    try:
        if subject is not None:
            update_data.update({"subject_id": subject.id})
        class_room.update_and_save(**update_data)
        class_room.save()
        log_activity(
            teacher,
            "update",
            "school_class",
            class_room.id,
            {},
            f"Updated class {class_room.name}",
        )
        return json_response({"message": "Update classroom succeeded!"})
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return json_response({"message": str(e)}, 500)


@school_class_router.post("/school_class/{class_id}/student")
def school_class_student_add(
    class_id: int,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    data: Dict[str, Any] = Body(None),
):
    school_class = SchoolClassModel.query.filter_by(id=class_id).first()
    if not school_class:
        return error_response("School class room doesn't exist", 404)

    data = data or {}
    try:
        student = Student.query.filter_by(email=data.get("email")).first()
        if student is None:
            student = Student(**data)
            student.save()

        if not school_class.has_student(student):
            school_class.add_student(student)
            school_class.save()
            log_activity(
                teacher,
                "create",
                "student_attended_class",
                school_class.id,
                {},
                f"Added student {student.full_name} to class {school_class.name}",
            )

        if not student.confirmed:
            send_student_confirmation_instructions.apply_async(args=[student.id])

    except exc.IntegrityError:
        return error_response("Student missing required data.", 400)
    except exc.DatabaseError as e:  # noqa
        return error_response("Server got an error.", 500)
    else:
        return json_response(
            {
                "message": "An invite to the student was sent",
                "status": "success",
            },
            201,
        )


@school_class_router.delete("/school_class/{class_id}/student")
def school_class_student_remove(
    class_id: int,
    student_id: int,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
):
    school_class = SchoolClassModel.query.filter_by(id=class_id).first()
    if not school_class:
        return error_response("School class room doesn't exist", 404)

    try:
        school_class.remove_student(student_id)
        log_activity(
            teacher,
            "delete",
            "student_attended_class",
            school_class.id,
            {},
            f"Deleted student from class {school_class.name}",
        )
    except Exception as e:  # noqa: BLE001
        logger.error(e)
        return error_response("Server got an error.", 500)
    else:
        return json_response(
            {"message": "Student removed.", "status": "success"}, 204
        )


@school_class_router.patch("/school_class/{class_id}/student")
def school_class_student_update_email(
    class_id: int,
    teacher: Teacher = Depends(jwt_required(fresh=True)),
    data: Dict[str, Any] = Body(None),
):
    school_class = SchoolClassModel.query.filter_by(id=class_id).first()
    if not school_class:
        return error_response("School class room doesn't exist", 404)

    data = data or {}
    validation = PatchPayloadSchema().validate(data=data)
    if validation is not None and len(validation) != 0:
        return error_response("Data is not valid!", 400)

    new_email = data.get("new_email")
    old_email = data.get("old_email")

    student = Student.query.filter_by(email=old_email).first()
    if not student:
        return error_response("Student not found!", 404)

    try:
        if student.confirmed:
            student.confirmed = False

        student.update_email(new_email)
        log_activity(
            teacher,
            "update",
            "student_attended_class",
            school_class.id,
            {},
            f"Updated student {student.full_name} from class {school_class.name}",
        )
        send_student_confirmation_instructions.apply_async(args=[student.id])

    except exc.DatabaseError as e:  # noqa
        return error_response("Server got an error.", 500)
    else:
        return json_response(
            {
                "message": f"Student email successfully updated! We have sent a confirmation email to {new_email}.",  # noqa
                "status": "success",
            }
        )
