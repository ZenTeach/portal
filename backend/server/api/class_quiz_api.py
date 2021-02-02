
import re
from typing import Dict

from flask import Blueprint, abort, jsonify, make_response, request, send_file
from flask.wrappers import Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource
from marshmallow import INCLUDE, Schema, ValidationError, fields
from server import db
from server.api import logger, report_5xx_error
from server.decorators import with_required_roles
from server.models import ClassQuiz as ClassQuizModel
from server.models import (ClassQuizSchema, ClassQuizStatus, QuizGrade,
                           QuizGradeSchema, StudentSchema, Teacher)
from server.tasks import (generate_pdf, send_quiz_generation_email,
                          send_quiz_pdf)
from sqlalchemy import exc

class_quiz_blueprint = Blueprint("class_quiz", __name__)
api = Api(class_quiz_blueprint)
dumper = ClassQuizSchema()
students_dumper = StudentSchema(many=True)


class ClassQuizCreateQuestionChoicesSchema(Schema):
    class Meta:
        unknown = INCLUDE

    uuid = fields.Str(required=True)
    value = fields.Str(required=True)


class ClassQuizCreateQuestionsSchema(Schema):
    class Meta:
        unknown = INCLUDE

    knowledge_item = fields.Str(required=True)
    question_type = fields.Int(required=True)
    choices = fields.Nested(ClassQuizCreateQuestionChoicesSchema, many=True, required=True)
    topic = fields.Str(required=True)
    subject = fields.Str(required=True)
    tag = fields.Str(required=True)
    question = fields.Str(required=True)
    id = fields.Int(required=True)


class ClassQuizCreateSchema(Schema):
    class Meta:
        unknown = INCLUDE

    subject = fields.Str(required=True)
    class_id = fields.Int(required=True)
    questions = fields.Nested(ClassQuizCreateQuestionsSchema, many=True, required=True)


class ClassQuiz(Resource):
    def get(self, class_quiz_uuid):
        error_response = {"message": "No Class Quiz found."}
        try:
            class_quiz = ClassQuizModel.query.filter_by(
                uuid=class_quiz_uuid).first()
            if not class_quiz:
                return make_response(error_response, 404)
            else:
                response_message = {
                    "status": "success",
                    "data": dumper.dump(class_quiz),
                }
                return make_response(response_message, 200)
        except ValueError:
            return make_response(error_response, 404)

    @with_required_roles(["Teacher", "Admin"])
    @jwt_required
    def delete(self, class_quiz_id):
        error_response = {"message": "No Class Quiz found."}
        try:
            class_quiz = ClassQuizModel.query.filter_by(
                id=class_quiz_id).first()
            if not class_quiz:
                return make_response(error_response, 404)
            else:
                db.session.delete(class_quiz)
                db.session.commit()
                response_message = {"status": "success",
                                    "message": "Deleted Quiz"}
                return make_response(response_message, 200)
        except exc.DatabaseError as e:  # noqa
            return make_response(error_response, 404)


class ClassQuizList(Resource):
    @with_required_roles(["Teacher", "Admin"])
    @jwt_required
    def get(self):
        return make_response(
            {
                "status": "success",
                "data": {
                    "class_quizzes": [
                        dumper.dump(classquiz)
                        for classquiz in ClassQuizModel.query.all()
                    ]
                },
            },
            200,
        )

    @jwt_required
    def post(self) -> Response:
        post_data: Dict = request.get_json()
        teacher_email = get_jwt_identity()['identity']["email"]
        error_object = {"status": "Failed", "message": "Quiz data not given."}
        if not post_data:
            return make_response(error_object, 400)
        validation_errors = None
        try:
            validation_errors = ClassQuizCreateSchema().validate(data=post_data)

            if validation_errors is not None and len(validation_errors) != 0:
                raise ValidationError("Malformed data")

            subject = post_data.get("subject")
            class_id = post_data.get("class_id")
            # TODO: Validate if questions exist in db
            questions = post_data.get("questions")

            quiz = ClassQuizModel(
                subject=subject,
                class_id=class_id,
                questions=questions,
            )

            quiz.save()
            response_object = {"status": "success",
                               "message": "Quiz was added!"}
            send_quiz_generation_email.apply_async(args=[teacher_email, quiz.id])
            return make_response(response_object, 201)
        except ValidationError:
            # "message": [i for x in  validation_errors.values() for i in x] # flatten errors
            return make_response(jsonify({
                "status": "failed",
                "message": validation_errors
            }), 400)
        except exc.IntegrityError as e:
            db.session.rollback()
            logger.error(e)
            report_5xx_error(e)
            return make_response(jsonify({
                "status": "failed",
                "message": "Quiz couldn't be created!"
            }), 500)


@api.resource("/class_quiz/pdf_view/<class_quiz_id>")
class ClassQuizPDFView(Resource):
    @jwt_required
    def get(self, class_quiz_id):
        quiz = ClassQuizModel.query.filter_by(id=class_quiz_id).first()
        error_object = {"status": "fail", "message": "Invalid payload."}
        if not quiz:
            return make_response(error_object, 400)

        generated_file_name = None
        try:
            generated_file_name = generate_pdf.delay(quiz)
        except Exception as e:
            logger.exception(e)
            report_5xx_error(e)
            error_object["message"] = "Error generating quiz pdf"
            return make_response(error_object, 500)

        return generated_file_name, 200


@api.representation("application/pdf")
def output_pdf(data, code, headers=None):
    return send_file(data, as_attachment=True)


class ClassQuizGenerator(Resource):
    @jwt_required
    def post(self, class_quiz_uuid):
        """
            Args:
                :type - generated document form
        """

        error_object = {"status": "Failed",
                        "message": "Failed to generate quiz"}

        teacher = get_jwt_identity()["identity"]
        quiz_id = ClassQuizModel.query.filter_by(uuid=class_quiz_uuid).first().id
        req_data = request.get_json()
        if req_data["type"] == "pdf":
            generated_file_name = None
            try:
                generated = generate_pdf.delay(quiz_id)
                generated_file_name = generated.get()
                send_quiz_pdf.apply_async(
                    args=[teacher["email"], generated_file_name])
            except Exception as e:
                logger.exception(e)
                error_object["message"] = "Error generating quiz pdf"
                report_5xx_error(e)
                return make_response(error_object, 500)
            return make_response(
                jsonify({
                    "status": "Succeeded",
                    "message": "Generated quiz!"
                }),
                200)
        elif req_data["type"] == "gform":
            t = Teacher.query.filter_by(email=teacher["email"]).first()
            teacher_uid = str(t.uuid)  # noqa
            script_id = None
            try:
                pass
            except Exception as e:
                logger.exception(e)
                error_object["message"] = "Error generating Google Form"
                report_5xx_error(e)
                return make_response(error_object, 500)
            return make_response(
                jsonify(
                    {
                        "status": "Success",
                        "message": "Generated quiz!",
                        "ScriptId": script_id,
                    }
                ),
                200,
            )
        else:
            return make_response(jsonify(error_object), 400)


class QuizReportCard(Resource):
    @jwt_required
    def get(self, uuid):
        # Validate the UUID string
        # Taken from https://stackoverflow.com/questions/7905929/how-to-test-valid-uuid-guid
        validator = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}$')
        if validator.match(uuid) is None:
            abort(400, 'Report Card id given is unknown or malformed')

        hyphen_count = uuid.count('-')
        if hyphen_count > 0:
            uuid = uuid.replace('-', '')

        grade = QuizGrade.query.filter_by(uuid=uuid).first()
        if not grade:
            abort(404, "Student or quiz don't exist.")

        return make_response(jsonify(grade.grade_breakdown), 200)


class GradedQuizzes(Resource):
    @jwt_required
    def get(self, quizUUId):
        quizId = ClassQuizModel.query.filter_by(uuid=quizUUId).first().id
        graded_quizzes = QuizGrade.query.filter_by(class_quiz_id=quizId, graded=True).all()
        if not graded_quizzes or len(graded_quizzes) == 0:
            abort(404, "No Quiz grading found!")

        # TODO: Check against non-existing student email
        serializer = QuizGradeSchema(many=True)
        return make_response(jsonify(serializer.dump(graded_quizzes)), 200)


class QuizAttendedStudents(Resource):
    @jwt_required
    def get(self, class_quiz_uuid):
        quiz = ClassQuizModel.query.filter_by(
            uuid=class_quiz_uuid, status=ClassQuizStatus.administered
        ).first()
        if len(quiz.student_quiz_grades) == 0:
            abort(404, "Student or quiz don't exist.")

        students = quiz.student_quiz_grades
        responses = students_dumper.dump(students)

        return make_response(jsonify(responses))


api.add_resource(ClassQuiz, "/class_quiz/<string:class_quiz_uuid>")
api.add_resource(ClassQuizGenerator,
                 "/class_quiz/<string:class_quiz_uuid>/generate")
api.add_resource(ClassQuizList, "/class_quiz")
api.add_resource(QuizReportCard, "/class_quiz/report_card/<string:uuid>")
api.add_resource(
    QuizAttendedStudents, "/class_quiz/<string:class_quiz_uuid>/attended_students"
)
api.add_resource(GradedQuizzes, "/class_quiz/<string:quizUUId>/graded")
