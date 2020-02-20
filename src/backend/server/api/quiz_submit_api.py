from flask import make_response, jsonify, Blueprint, request, abort
from flask_restful import Resource, Api, reqparse
import json
from server.models import class_quiz_score, ClassQuiz as ClassQuizModel, Student, ClassQuizStatus
from server import db
from sqlalchemy import exc

quiz_submit_blueprint = Blueprint('quiz_submit', __name__)
api = Api(quiz_submit_blueprint)

parser = reqparse.RequestParser()
parser.add_argument('email', required=True,
                    help="Student Email")

parser.add_argument('quiz', required=True,
                    help="Quiz unique id")


class SubmitQuiz(Resource):
    def get(self):
        """
            Creates a quiz session object
        """
        # Find student with ID
        args = parser.parse_args()
        student = Student.query.filter_by(email=args['email']).first()
        if not student:
            abort(404, "Student email doesn't exist")

        # add session to class_quiz
        class_quiz = ClassQuizModel.query.filter_by(uuid=args['quiz'])

        if not class_quiz:
            abort(404, "Class Quiz doesn't exist")

        class_quiz.add_student_session(student)
        return make_response(jsonify({
            'message': 'Created a new session!',
            'status': 'success'
        }))

    def post(self):
        post_data = request.get_json()
        # Step 1: Validate data
        student = Student.query.filter_by(email=post_data.get('StudentEmail')).first()
        if student is None:
            abort(404, f"Student with email {post_data.get('StudentEmail')} doesn't exist")

        class_quiz = ClassQuizModel.query.filter_by(uuid=post_data.get('QuizId')).first()
        if class_quiz is None:
            abort(404, "Class Quiz doesn't exist")

        try:
            # Step 2: Store
            insert_statement = class_quiz_score.insert().values(student_id = student.id,
                                            quiz_id=class_quiz.id,
                                            responses=post_data.get('data'))
            # db.session.add()
            db.session.execute(insert_statement)
            # TODO: Fix! This logic is somehow flawed as the first submission
            # triggers a model update.
            # Proposal: Add a background job to be executed only when all the
            # quizzes have been submitted.
            class_quiz.update_status(ClassQuizStatus.administered)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Quiz submitted!'
            }
            return make_response(response_object, 201)
        # Step 3: Update
        except exc.IntegrityError as e:
            print(e)
            return make_response(jsonify({
                'status': 'error',
                'message': 'Encountered a server error'
            }), 500)

api.add_resource(SubmitQuiz, '/submit_quiz')
