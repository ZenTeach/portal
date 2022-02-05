
from flask import Blueprint, jsonify, make_response, request
from flask.views import MethodView
from flask_jwt_extended import current_user
from server.api import log_activity, logger
from server.models import ClassQuiz as ClassQuizModel
from server.models import (ClassQuizStatus, QuizSession, QuizSessionStatus,
                           Student)
from server.tasks import grader_administered_quizzes
from sqlalchemy import exc
from webargs import fields, validate
from webargs.flaskparser import use_kwargs

quiz_submit_blueprint = Blueprint("quiz_submit", __name__)

quiz_submit_args = {
    'email': fields.Str(required=True, validate=validate.Email()),
    'quiz': fields.Str(required=True)
}


class SubmitQuiz(MethodView):
    @use_kwargs(quiz_submit_args, location='query')
    def get(self, email, quiz):
        """
            Creates a quiz session object
        """

        student = Student.query.filter_by(email=email).first()
        if not student:
            return make_response(jsonify({'message': "Student email doesn't exist"}), 404)

        if not student.confirmed:
            return make_response(jsonify({
                'message': "Email address hasn't been verified yet!"
            }), 400)

        class_quiz = ClassQuizModel.query.filter_by(uuid=quiz).first()
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
                class_quiz.add_student_session(student)
                class_quiz.save()
                log_activity(
                    current_user,
                    'create',
                    'quiz_session',
                    class_quiz.id,
                    f'{student.full_name} has started a quiz session for {class_quiz.name}')
        except exc.DatabaseError as e:
            logger.error(e)
            return make_response(
                jsonify({
                    "message": "Couldn't create a new quiz session.",
                    "status": "error",
                }),
                500)
        else:
            return make_response(
                jsonify({"message": "Created a new session!",
                         "status": "success"}), 200
            )

    def post(self):
        post_data = request.get_json()
        student_email = post_data.get('StudentEmail')
        class_quiz_id = post_data.get('QuizId')
        student_response = post_data.get('data')

        if len(student_response) == 0:
            return make_response(jsonify({
                'message': "Cannot submit quiz without any choices selected"
            }), 400)

        student = Student.query.filter_by(email=student_email).first()
        class_quiz = ClassQuizModel.query.filter_by(uuid=class_quiz_id).first()

        if student is None:
            return make_response(jsonify({
                'message': "Student with email {} doesn't exist".format(student_email)
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

            student.add_quiz_score(class_quiz, student_response)
            student.save()

            class_quiz.update_status(ClassQuizStatus.administered)
            quiz_session.update_status(QuizSessionStatus.ended)
            log_activity(
                current_user,
                'update',
                'quiz_session',
                class_quiz.id,
                f'{student.full_name} has completed a quiz session for {class_quiz.name}')
            grader_administered_quizzes.apply_async(args=[quiz_session.uuid])

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
