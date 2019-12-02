from sqlalchemy import exc
from flask import Blueprint, request, make_response, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource, Api
import json


from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

from server.decorators import with_required_roles
from server.models import ClassQuiz as ClassQuizModel, ClassQuizSchema
from server import db, mail
from server.tasks import generate_pdf, send_quiz_pdf
from server.api import api_logger

class_quiz_blueprint = Blueprint('class_quiz', __name__)
api = Api(class_quiz_blueprint)
dumper = ClassQuizSchema()


class ClassQuiz(Resource):
    @jwt_required
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
                    'data': dumper.dump(class_quiz)
                }
                return make_response(response_message, 200)
        except ValueError:
            return make_response(error_response, 404)


class ClassQuizList(Resource):
    @with_required_roles(["Teacher", "Admin"])
    @jwt_required
    def get(self):
        return make_response({
            'status': 'success',
            'data': {
                'class_quizzes': [dumper.dump(classquiz) for classquiz in ClassQuizModel.query.all()]
            }
        }, 200)

    @jwt_required
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
        variants = post_data.get('variants')
        questions = post_data.get('questions')
        try:
            db.session.add(ClassQuizModel(subject=subject, max_score=max_score,
                                          class_id=class_id, variants=variants, questions=questions))
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Quiz was added!'
            }
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


@api.resource('/class_quiz/pdf_view/<class_quiz_id>')
class ClassQuizPDFView(Resource):
    @jwt_required
    def get(self, class_quiz_id):
        quiz = ClassQuizModel.query.filter_by(id=class_quiz_id).first()
        error_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        if not quiz:
            return make_response(error_object, 400)

        generated_file_name = None
        try:
            generated_file_name = generate_pdf.delay(quiz)
        except Exception as e:
            api_logger.exception(e)
            error_object["message"] = "Error generating quiz pdf"
            return make_response(error_object, 500)

        return generated_file_name, 200


@api.representation("application/pdf")
def output_pdf(data, code, headers=None):
    return send_file(data, as_attachment=True)


class ClassQuizGenerator(Resource):
    @jwt_required
    def post(self, class_quiz_id):
        """
            Args:
                :type - generated document form
        """

        error_object = {
            'status': 'Failed',
            'message': 'Failed to generate quiz'
        }

        teacher = get_jwt_identity()['identity']
        req_data = request.get_json()
        if req_data["type"] == "pdf":
            generated_file_name = None
            try:
                generated = generate_pdf.delay(class_quiz_id)
                generated_file_name = generated.get()
                send_quiz_pdf.apply_async(args=[teacher['email'], generated_file_name])
            except Exception as e:
                api_logger.exception(e)
                error_object["message"] = "Error generating quiz pdf"
                return make_response(error_object, 500)
            return make_response(jsonify({
                'status': 'Succeeded',
                'message': 'Failed to generate quiz'
            }), 200)
        elif req_data["type"] == "gform":
            pass
        else:
            return make_response(jsonify(error_object), 400)

api.add_resource(ClassQuizPing, '/class_quiz/ping')
api.add_resource(ClassQuiz, '/class_quiz/<int:class_quiz_id>')
api.add_resource(ClassQuizGenerator, '/class_quiz/<int:class_quiz_id>/generate')
api.add_resource(ClassQuizList, '/class_quiz')
