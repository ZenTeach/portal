from sqlalchemy import exc
from flask import Blueprint, request, make_response
from flask_restful import Resource, Api
import json

from server.decorators import with_required_roles
from server.models import ClassQuiz as ClassQuizModel
from server import db

class_quiz_blueprint = Blueprint('class_quiz', __name__)
api = Api(class_quiz_blueprint)


class ClassQuiz(Resource):
    @with_required_roles(["Teacher", "Admin"])
    def get(self, class_quiz_id):
        error_response = {
            'message': 'No Class Quiz found.'
        }
        try:
            class_quiz = ClassQuizModel.query.filter_by(
                id=class_quiz_id).first()
            if not class_quiz:
                return make_response(error_response, 404)
            else:
                response_message = {
                    'status': 'success',
                    'data': class_quiz.to_json()
                }
                return make_response(response_message, 200)
        except ValueError:
            return make_response(error_response, 404)


class ClassQuizList(Resource):
    @with_required_roles(["Teacher", "Admin"])
    def get(self):
        return make_response({
            'status': 'success',
            'data': {
                'class_quizzes': [classquiz.to_json for classquiz in ClassQuizModel.query.all()]
            }
        }, 200)

    def post(self):
        post_data = request.get_json()
        error_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not post_data:
            return make_response(error_object, 400)
        subject = post_data.get('subject')
        max_score = post_data.get('max_score')
        class_id = post_data.get('class_id')
        questions_list = post_data.get('questions_list')
        try:
            db.session.add(ClassQuizModel(subject=subject, max_score=max_score,
                                          class_id=class_id, questions_list=questions_list))
            db.session.commit()
            response_object['status'] = 'success'
            response_object['message'] = 'Quiz was added!'
            return make_response(response_object, 201)
        except exc.IntegrityError:
            db.session.rollback()
            return make_response(response_object, 400)


class ClassQuizPing(Resource):
    def get(self):
        return make_response({
            'status': 'success',
            'message': 'Pinged Class Quiz'
        }, 200)


api.add_resource(ClassQuizPing, '/class_quiz/ping')
api.add_resource(ClassQuiz, '/class_quiz/<class_quiz_id>')
api.add_resource(ClassQuizList, '/class_quiz')
