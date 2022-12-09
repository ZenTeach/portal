
import re
from typing import Dict, NoReturn, Union
from uuid import UUID

from flask import Blueprint, abort, jsonify, make_response, request
from flask.views import MethodView
from flask.wrappers import Response
from flask_jwt_extended import current_user, jwt_required
from marshmallow import (INCLUDE, Schema, ValidationError, fields,
                         validates_schema)
from server import db
from server.api import log_activity, logger
from server.decorators import with_required_roles
from server.models import ClassQuiz as ClassQuizModel
from server.models import (ClassQuizSchema, ClassQuizStatus, Questions,
                           QuizGrade, QuizGradeSchema, QuizSession,
                           StudentSchema)
from server.tasks import send_quiz_generation_email, send_report_card_pdf
from sqlalchemy import exc

class_quiz_blueprint = Blueprint("class_quiz", __name__)
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

    knowledge_item = fields.Nested(ClassQuizCreateKnowledgeItemSchema,
                                   required=True, unknown=INCLUDE)
    question_type = fields.Int(required=True)
    choices = fields.Nested(ClassQuizCreateQuestionChoicesSchema, many=True, required=True)
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
        question_ids = [question['id'] for question in data['questions']]
        questions = Questions.query.filter(Questions.id.in_(question_ids))
        if questions.count() != len(question_ids):
            raise ValidationError('Invalid question found! Please report this so we can fix it!')


class ClassQuizUpdateSchema(Schema):
    class Meta:
        unknown = INCLUDE

    name = fields.Str(required=True)
    private = fields.Boolean(required=False)


class ClassQuiz(MethodView):
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
    @jwt_required(fresh=True)
    def delete(self, class_quiz_id):
        error_response = {"message": "No Class Quiz found."}
        try:
            class_quiz = ClassQuizModel.query.filter_by(
                id=class_quiz_id).first()
            if not class_quiz:
                return make_response(error_response, 404)
            else:
                class_quiz_id = class_quiz.id
                class_quiz.delete()
                log_activity(
                    current_user,
                    'delete',
                    'class_quiz',
                    class_quiz_id,
                    {},
                    'Deleted Class Quiz.'
                )
                response_message = {"status": "success",
                                    "message": "Deleted Quiz"}
                return make_response(response_message, 200)
        except exc.DatabaseError as e:  # noqa
            return make_response(error_response, 404)

    @jwt_required(fresh=True)
    def patch(self, class_quiz_uuid):
        post_data: Dict = request.get_json()
        error_object = {"status": "Failed", "message": "Quiz data not given."}
        if not post_data:
            return make_response(error_object, 400)
        validation_errors = None
        class_quiz: ClassQuiz = ClassQuizModel.query.filter_by(
            uuid=class_quiz_uuid).first()
        try:
            validation_errors = ClassQuizUpdateSchema().validate(data=post_data)
            if validation_errors is not None and len(validation_errors) != 0:
                raise ValidationError("Malformed data")
            class_quiz.update_and_save(**post_data, refresh=True)
            log_activity(
                current_user,
                'update',
                'class_quiz',
                class_quiz.id,
                {},
                'Updated Class Quiz.'
            )
            return make_response(jsonify({
                'status': 'updated',
                'message': 'Quiz updated'
            }), 200)
        except ValidationError:
            # "message": [i for x in  validation_errors.values() for i in x] # flatten errors
            return make_response(jsonify({
                "status": "failed",
                "message": validation_errors
            }), 400)
        except Exception as e:
            logger.error(e)
            return make_response(jsonify({
                "status": "failed",
                "message": "Quiz couldn't be updated!"
            }), 500)


class ClassQuizList(MethodView):
    @with_required_roles(["Teacher", "Admin"])
    @jwt_required(fresh=True)
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

    @jwt_required(fresh=True)
    def post(self) -> Response:
        post_data: Dict = request.get_json()
        teacher_email = current_user.email
        error_object = {"status": "Failed", "message": "Quiz data not given."}
        if not post_data:
            return make_response(error_object, 400)
        validation_errors = None
        try:
            validation_errors = ClassQuizCreateSchema().validate(data=post_data)

            if validation_errors is not None and len(validation_errors) != 0:
                raise ValidationError("Malformed data")

            quiz = ClassQuizModel(**post_data)

            quiz.save()
            log_activity(
                current_user,
                'create',
                'class_quiz',
                quiz.id,
                {},
                f'{current_user} created a quiz for class {quiz.class_id}',
            )
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
            return make_response(jsonify({
                "status": "failed",
                "message": "Quiz couldn't be created!"
            }), 500)


class QuizReportCard(MethodView):
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
        total_score = ''
        grade = QuizGrade.query.filter_by(uuid=uuid).first()
        if not grade:
            session = QuizSession.query.filter_by(uuid=uuid).first()
            if not session:
                abort(404, "Student or quiz don't exist.")
            else:
                student = session.student
                grade = QuizGrade.query.filter_by(
                    class_quiz_id=session.class_quiz_id).filter_by(
                        student_id=student.id
                ).first()
        total_score = f"{grade.score}/{grade.class_quiz.max_score}"
        return make_response(jsonify({
            'report_card': grade.grade_breakdown,
            'score': total_score
        }), 200)


class GradedQuizzes(MethodView):
    @jwt_required(fresh=True)
    def get(self, quizUUId):
        quizId = ClassQuizModel.query.filter_by(uuid=quizUUId).first().id
        graded_quizzes = QuizGrade.query.filter_by(class_quiz_id=quizId, graded=True).all()

        serializer = QuizGradeSchema(many=True)
        return make_response(jsonify(serializer.dump(graded_quizzes)), 200)


class QuizAttendedStudents(MethodView):
    @jwt_required(fresh=True)
    def get(self, class_quiz_uuid):
        quiz = ClassQuizModel.query.filter_by(
            uuid=class_quiz_uuid, status=ClassQuizStatus.administered
        ).first()
        if len(quiz.student_quiz_grades) == 0:
            abort(404, "Student or quiz don't exist.")

        students = quiz.student_quiz_grades
        responses = students_dumper.dump(students)

        return make_response(jsonify(responses))


class SendReportCard(MethodView):
    @jwt_required(fresh=True)
    def get(self, quizGradeUUID: UUID) -> Union[Response, NoReturn]:
        grade = QuizGrade.query.filter_by(uuid=quizGradeUUID).first()

        if not grade:
            abort(404, "Report card not found!")

        try:
            send_report_card_pdf.apply_async(args=[grade.uuid])
        except Exception:
            abort(500, "Server run into an error sending report card. We're working to resolve the issue")  # noqa
        else:
            return make_response(jsonify({
                "status": "success",
                "message": "Report card email has been sent!",
            }), 200)


class_quiz_blueprint.add_url_rule(
    "/class_quiz/<string:class_quiz_uuid>", view_func=ClassQuiz.as_view('class_quiz_with_id'))
class_quiz_blueprint.add_url_rule("/class_quiz", view_func=ClassQuizList.as_view('class_quiz'))
class_quiz_blueprint.add_url_rule(
    "/class_quiz/report_card/<string:uuid>",
    view_func=QuizReportCard.as_view('class_quiz_report_card'))
class_quiz_blueprint.add_url_rule(
    "/class_quiz/<string:class_quiz_uuid>/attended_students",
    view_func=QuizAttendedStudents.as_view('class_quiz_students')
)
class_quiz_blueprint.add_url_rule(
    "/class_quiz/<string:quizUUId>/graded", view_func=GradedQuizzes.as_view('graded_class_quiz'))
class_quiz_blueprint.add_url_rule("/class_quiz/<string:quizGradeUUID>/send_report",
                                  view_func=SendReportCard.as_view("send_quiz_report_card"))
