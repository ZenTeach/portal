
from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import INCLUDE, Schema, fields
from server import db
from server.api import logger, report_5xx_error
from server.decorators import with_required_roles
from server.models import SchoolClass as SchoolClassModel
from server.models import SchoolClassSchema, Student
from server.tasks import send_student_confirmation_instructions
from sqlalchemy import exc
from webargs import fields as webarg_fields
from webargs.flaskparser import use_kwargs

school_class_blueprint = Blueprint("school_class", __name__)
schema_dumper = SchoolClassSchema()
student_delete_args = {
    'student_id': webarg_fields.Int(required=True)
}


class PatchPayloadSchema(Schema):
    class Meta:
        unknown = INCLUDE

    new_email = fields.Email(required=True)
    old_email = fields.Email(required=True)


class SchoolClass(MethodView):
    @jwt_required
    def get(self, school_class_id):
        error_response = jsonify({"message": "Class room doesn't exist"})
        try:
            class_room = SchoolClassModel.query.filter_by(
                id=school_class_id
            ).first()
            if not class_room:
                return make_response(error_response, 404)
            else:
                response_object = jsonify(
                    {"status": "success",
                        "data": schema_dumper.dump(class_room)}
                )
            return make_response(response_object, 200)
        except ValueError:
            return make_response(error_response, 404)

    @jwt_required
    def delete(self, school_class_id):
        try:
            class_room = SchoolClassModel.query.filter_by(id=school_class_id).first()

            if not class_room:
                return make_response(jsonify({
                    'status': 'failure',
                    'message': 'Classroom not found'
                }), 404)

            SchoolClassModel.remove_classroom(class_room)
            return make_response(jsonify({
                'status': 'success',
                'message': 'Classroom was successfully deleted.'
            }), 204)
        except Exception as e:
            logger.error(e)
            report_5xx_error(e)
            return make_response(jsonify({
                'status': 'success',
                'message': 'Encountered an error while deleting classroom.'
            }), 500)

    @jwt_required
    def put(self, school_class_id):
        update_data = request.get_json()
        error_response = jsonify({"message": "Class room doesn't exist"})
        class_room = SchoolClassModel.query.filter_by(
            id=school_class_id).first()

        if not class_room:
            return make_response(error_response, 404)

        try:
            class_room.update_from_dict(update_data)
            class_room.save()
            return make_response(jsonify({
                'message': 'Update classroom succeeded!'
            }), 200)
        except Exception as e:
            logger.error(e)
            report_5xx_error(e)
            return make_response(jsonify({
                'message': str(e)
            }), 500)


class SchoolClassList(MethodView):
    @jwt_required
    def get(self):
        response_object = jsonify(
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
        return make_response(response_object, 200)

    @jwt_required
    def post(self):
        post_data = request.get_json()
        error_object = jsonify(
            {"status": "fail", "message": "Invalid payload."})
        teacher = get_jwt_identity()["identity"]
        if not post_data:
            return make_response(error_object, 400)
        name = post_data.get("name")
        subject = post_data.get("subject")
        start_date = post_data.get("start_date")
        exam_board = post_data.get("exam_board")
        year_group = post_data.get("year_group")
        teacher_id = teacher["id"]
        try:
            school_class = SchoolClassModel.query.filter_by(name=name).first()
            if not school_class:
                school_class = SchoolClassModel(
                    name=name,
                    subject=subject,
                    exam_board=exam_board,
                    start_date=start_date,
                    teacher_id=teacher_id,
                    year_group=year_group
                )
                school_class.save()
                response_object = jsonify(
                    {"status": "success",
                        "message": "{} was added!".format(name)}
                )
                return make_response(response_object, 201)
            else:
                error_object.message = "School class already exists."
                return make_response(error_object, 400)
        except exc.IntegrityError as err:  # noqa
            db.session.rollback()
            report_5xx_error(err)
            return make_response(error_object, 500)


class SchoolClassOwned(MethodView):
    @jwt_required
    @with_required_roles(["Admin"])
    def get(self, teacher_id):
        error_message = jsonify({"message": "Class room doesn't exist"})
        try:
            classrooms = SchoolClassModel.query.filter_by(
                teacher_id=int(teacher_id)
            ).all()
            if not classrooms:
                return make_response(error_message, 404)
            else:

                response_object = jsonify({
                    "status": "success",
                    "data": [
                        schema_dumper.dump(c) for c in classrooms
                    ]
                })
                return make_response(response_object, 200)
        except ValueError:
            return make_response(error_message, 400)


class TeacherOwnedClass(MethodView):
    @jwt_required
    def get(self):
        error_object = {"message": ""}
        try:
            teacher = get_jwt_identity()["identity"]
            classrooms = SchoolClassModel.query.filter_by(
                teacher_id=int(teacher["id"])
            )

            if not classrooms:
                error_object["message"] = "No class rooms found"
                return make_response(jsonify(error_object), 200)
            else:
                response_object = jsonify({
                    "status": "success",
                    "data": [
                        schema_dumper.dump(c) for c in classrooms
                    ]
                })
                return make_response(response_object, 200)
        except Exception as e:
            from server.api import logger
            report_5xx_error(e)
            logger.debug(e)
            error_object["message"] = "Error processing request"
            return make_response(jsonify(error_object), 500)


class SchoolClassStudent(MethodView):
    @jwt_required
    def post(self, class_id):
        school_class = SchoolClassModel.query.filter_by(id=class_id).first()
        if not school_class:
            return make_response(jsonify({
                'message': "School class room doesn't exist"
            }), 404)

        data = request.get_json()
        try:
            student = Student.query.filter_by(email=data.get('email')).first()
            if student is not None:
                pass
            else:
                student = Student(**data)
                student.save()

            if not school_class.has_student(student):
                school_class.add_student(student)
                school_class.save()

            send_student_confirmation_instructions.apply_async(args=[student.id])
        except exc.IntegrityError:
            return make_response(jsonify({
                'message': "Student missing required data."
            }), 400)
        except exc.DatabaseError as e:  # noqa
            report_5xx_error(e)
            return make_response(jsonify({'message': "Server got an error."}), 500)
        else:
            return make_response(
                jsonify(
                    {
                        "message": "An invite to the student was sent",
                        "status": "success",
                    }
                ),
                201,
            )

    @jwt_required
    @use_kwargs(student_delete_args, location='query')
    def delete(self, class_id, student_id):
        school_class = SchoolClassModel.query.filter_by(id=class_id).first()
        if not school_class:
            return make_response(jsonify({
                'message': "School class room doesn't exist"
            }), 404)

        try:
            school_class.remove_student(student_id)
        except Exception as e:  # noqa
            logger.error(e)
            report_5xx_error(e)
            return make_response(jsonify({
                'message': "Server got an error."
            }), 500)
        else:
            return make_response(
                jsonify(
                    {
                        "message": "Student removed.",
                        "status": "success",
                    }
                ),
                204,
            )

    @jwt_required
    def patch(self, class_id):

        school_class = SchoolClassModel.query.filter_by(id=class_id).first()
        if not school_class:
            return make_response(jsonify({
                'message': "School class room doesn't exist"
            }), 404)

        data = request.get_json()
        validation = PatchPayloadSchema().validate(data=data)
        if validation is not None and len(validation) != 0:
            return make_response(jsonify({
                'message': "Data is not valid!"
            }), 400)

        new_email = data.get('new_email')
        old_email = data.get('old_email')

        student = Student.query.filter_by(email=old_email).first()
        if not student:
            return make_response(jsonify({
                'message': "Student not found!"
            }), 404)

        try:
            if student.confirmed:
                student.confirmed = False

            student.update_email(new_email)
            send_student_confirmation_instructions.apply_async(args=[student.id])

        except exc.DatabaseError as e:  # noqa
            report_5xx_error(e)
            return make_response(jsonify({
                'message': "Server got an error."
            }), 500)
        else:
            return make_response(
                jsonify(
                    {
                        "message": f"Student email successfully updated! We have sent a confirmation email to {new_email}.",  # noqa
                        "status": "success",
                    }
                ),
                200,
            )


school_class_blueprint.add_url_rule(
    "/school_class/<int:school_class_id>", view_func=SchoolClass.as_view('schoolclass'))
school_class_blueprint.add_url_rule(
    "/school_class/owned/<teacher_id>", view_func=SchoolClassOwned.as_view('teacher_owned_schoolclass'))  # noqa
school_class_blueprint.add_url_rule(
    "/school_class/owned", view_func=TeacherOwnedClass.as_view('owned_schoolclass'))
school_class_blueprint.add_url_rule(
    "/school_class", view_func=SchoolClassList.as_view('schoolclass_list'))
school_class_blueprint.add_url_rule(
    "/school_class/<int:class_id>/student", view_func=SchoolClassStudent.as_view('schoolclass_student')  # noqa
)
