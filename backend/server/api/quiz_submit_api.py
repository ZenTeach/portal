
from datetime import datetime

from flask import Blueprint, jsonify, make_response
from flask.views import MethodView
from marshmallow import Schema
from server.api import logger
from server.models import ClassQuiz as ClassQuizModel
from server.models import QuizSession, QuizSessionStatus, Student
from sqlalchemy import exc, func
from webargs import fields, validate
from webargs.flaskparser import use_kwargs

quiz_submit_blueprint = Blueprint("quiz_submit", __name__)

quiz_fetch_args = {
    'email': fields.Str(missing=""),
    'quiz': fields.UUID(required=True)
}


class quiz_submit_args(Schema):
    StudentEmail = fields.Str(validate=validate.Email())
    # TODO: look into data validation a setting custom http status code
    QuizId = fields.UUID()
    data = fields.List(fields.Dict, missing=[])


class SubmitQuiz(MethodView):
    @use_kwargs(quiz_fetch_args, location='query')
    def get(self, email, quiz):
        """
            Creates a quiz session object
        """

        student_email = email.lower()
        student = Student.query.filter(func.lower(Student.email) == student_email).first()
        class_quiz = ClassQuizModel.query.filter_by(uuid=quiz).first()
        success_response = {
            "message": "Created a new session!",
            "data": {},
            "status": "success"}

        if not student:
            # create an anonymous student if quiz is public
            if not class_quiz.private:
                student = Student.create_anonymous_student(
                    classes=[class_quiz.school_class],
                    confirmed=True
                )

                success_response["data"] = {
                    "anonymous_student_email": student.email,
                    "anonymous_student_password": "Asdfgh12!"
                }
            else:
                return make_response(jsonify({'message': "Student email doesn't exist"}), 404)

        if not student.confirmed:
            return make_response(jsonify({
                'message': "Email address hasn't been verified yet!"
            }), 400)

        if not class_quiz:
            return make_response(jsonify({"message": "Class Quiz doesn't exist"}), 404)

        try:
            submission = QuizSession.query.filter_by(
                student=student, class_quiz=class_quiz).first()
            if submission:
                if submission.has_session_ended():
                    return make_response(jsonify({
                        'message': "Quiz has already been submitted. If you think this is by mistake, contact your teacher for a redo."  # noqa
                    }), 400)  # noqa
            else:
                new_session = class_quiz.add_student_session(student)
                class_quiz.save()
                if not class_quiz.private:
                    # attach session to quiz response
                    success_response['data'].update({
                        'session_id': new_session.uuid
                    })
        except exc.DatabaseError as e:
            logger.error(e)
            return make_response(
                jsonify({
                    "message": "Couldn't create a new quiz session.",
                    "status": "error",
                }),
                500)
        else:
            return make_response(success_response, 200)

    @use_kwargs(quiz_submit_args(), location='json')
    def post(self, StudentEmail, QuizId, data):
        if len(data) == 0:
            return make_response(jsonify({
                'message': "Cannot submit quiz without any choices selected"
            }), 400)

        student = Student.query.filter_by(email=StudentEmail).first()
        class_quiz = ClassQuizModel.query.filter_by(uuid=QuizId).first()

        if student is None:
            return make_response(jsonify({
                'message': "Student with email {} doesn't exist".format(StudentEmail)
            }), 404)

        if class_quiz is None:
            return make_response(jsonify({
                'message': "Class Quiz doesn't exist"
            }), 404)

        quiz_session = QuizSession.query.filter_by(
            student_id=student.id, class_quiz_id=class_quiz.id
        ).first()

        if not quiz_session:
            return make_response(jsonify({
                'message': "Quiz not started"
            }), 404)
        try:
            if quiz_session.has_session_ended():
                return make_response(jsonify({
                    'message': "Session has ended!"
                }), 404)

            student.add_quiz_score(class_quiz, data)
            student.save()

            quiz_session.update_and_save(
                status=QuizSessionStatus.ended,
                end_time=datetime.now())

            response_object = {"status": "success",
                               "message": "Quiz submitted!"}
            return make_response(response_object, 201)
        except exc.IntegrityError as e:
            logger.error(e)
            return make_response(
                jsonify({
                    "status": "error",
                    "message": "Encountered a server error"
                }),
                500)


quiz_submit_blueprint.add_url_rule("/submit_quiz", view_func=SubmitQuiz.as_view('submit_quiz_api'))
