
from flask import Blueprint, abort, jsonify, make_response, request
from flask_restful import Api, Resource, reqparse
from server import db
from server.api import logger, report_5xx_error
from server.models import ClassQuiz as ClassQuizModel
from server.models import (ClassQuizStatus, QuizSession, QuizSessionStatus,
                           Student)
from server.tasks import grader_administered_quizzes
from sqlalchemy import exc

quiz_submit_blueprint = Blueprint("quiz_submit", __name__)
api = Api(quiz_submit_blueprint)

parser = reqparse.RequestParser()
parser.add_argument("email", required=True, help="Student Email")

parser.add_argument("quiz", required=True, help="Quiz unique id")


class SubmitQuiz(Resource):
    def get(self):
        """
            Creates a quiz session object
        """
        args = parser.parse_args()

        student = Student.query.filter_by(email=args["email"]).first()
        if not student:
            abort(404, "Student email doesn't exist")

        class_quiz = ClassQuizModel.query.filter_by(uuid=args["quiz"]).first()
        if not class_quiz:
            abort(404, "Class Quiz doesn't exist")

        try:
            submission = QuizSession.query.filter_by(
                student=student, class_quiz=class_quiz).first()
            if submission:
                if submission.has_session_ended():
                    abort(400, "Quiz has already been submitted. If you think this is by mistake, contact your teacher for a redo.")  # noqa
            else:
                class_quiz.add_student_session(student)
                class_quiz.save()
        except exc.DatabaseError as e:
            logger.error(e)
            report_5xx_error(e)
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
        # Step 1: Validate data
        student_email = post_data.get('StudentEmail')
        student = Student.query.filter_by(
            email=student_email).first()
        if student is None:
            abort(
                404,
                "Student with email {} doesn't exist".format(student_email)
            )

        class_quiz = ClassQuizModel.query.filter_by(
            uuid=post_data.get("QuizId")
        ).first()
        if class_quiz is None:
            abort(404, "Class Quiz doesn't exist")

        quiz_session = QuizSession.query.filter_by(
            student_id=student.id, class_quiz_id=class_quiz.id
        ).first()

        if not quiz_session:
            abort(404, "Quiz not started")
        try:
            # check if session ended
            if quiz_session.has_session_ended():
                abort(404, "Session has ended!")

            # Step 2: Store
            student.add_quiz_score(class_quiz, post_data.get("data"))
            student.save()
            # TODO: Fix! This logic is somehow flawed as the first submission
            # triggers a model update.
            # Proposal: Execute only once the due date is up!
            class_quiz.update_status(ClassQuizStatus.administered)
            # 1. End Quiz Session
            quiz_session.update_status(QuizSessionStatus.ended)
            # 2. Trigger background job
            grader_administered_quizzes.apply_async(args=[quiz_session.uuid])
            db.session.commit()
            response_object = {"status": "success",
                               "message": "Quiz submitted!"}
            return make_response(response_object, 201)
        # Step 3: Update
        except exc.IntegrityError as e:
            logger.error(e)
            report_5xx_error(e)
            return make_response(
                jsonify({
                    "status": "error",
                    "message": "Encountered a server error"
                }),
                500)


api.add_resource(SubmitQuiz, "/submit_quiz")
