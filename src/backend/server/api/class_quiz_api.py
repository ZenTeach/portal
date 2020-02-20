import json

from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Api, Resource
from jinja2 import Environment, FileSystemLoader
from server import db, mail
from server.api import api_logger
from server.decorators import with_required_roles
from server.models import ClassQuiz as ClassQuizModel
from server.models import ClassQuizSchema, Teacher
from server.tasks import (execute_app_script, generate_gform_quiz,
                          generate_pdf, send_google_form_email, send_quiz_pdf)
from sqlalchemy import exc
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

class_quiz_blueprint = Blueprint('class_quiz', __name__)
api = Api(class_quiz_blueprint)
dumper = ClassQuizSchema()


class ClassQuiz(Resource):
    @jwt_required
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

    @with_required_roles(["Teacher", "Admin"])
    @jwt_required
    def delete(self, class_quiz_id):
        error_response = {
            'message': 'No Class Quiz found.'
        }
        try:
            class_quiz = ClassQuizModel.query.filter_by(id=class_quiz_id).first()
            if not class_quiz:
                return make_response(error_response, 404)
            else:
                db.session.delete(class_quiz)
                db.session.commit()
                response_message = {
                    'status': 'success',
                    'message': "Deleted Quiz"
                }
                return make_response(response_message, 200)
        except expression as e:
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
            'status': 'Failed',
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


class ClassQuizGeneratorExecutor(Resource):
    @jwt_required
    def get(self, class_quiz_id, script_id):
        teacher_email = get_jwt_identity()['identity']['email']
        teacher = Teacher.query.filter_by(email=teacher_email).first()
        response = {
            'message':'',
            'status': ''
        }
        # if not teacher.owns_class(class_quiz):
        #     response['message'] = "The class doesn't exist for the logged in teacher."
        #     response['status'] = 'Failed'
        #     return make_response(jsonify(response), 404)

        try:
            script_execution_job = execute_app_script.apply_async(args=[script_id, teacher.uuid])
            published_url = script_execution_job.get()
            # TODO: send email with published url
        except Exception as e:
            response['message'] = "Encountered error."
            response['status'] = 'Failed'
            print(e)
            return make_response(jsonify(response), 500)
        print("Publised URL: {}", published_url)
        response['message'] = 'Succeeded generating quiz'
        response['status'] = 'Success'
        return make_response(jsonify(response), 200)


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
        # quiz = ClassQuizModel.query.filter_by(id=class_quiz_id).first()
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
                'message': 'Generated quiz!'
            }), 200)
        elif req_data["type"] == "gform":
            t = Teacher.query.filter_by(email=teacher["email"]).first()
            teacher_uid = str(t.uuid)
            script_id = None
            try:
                #gform_job = generate_gform_quiz.apply_async(args=[class_quiz_id, teacher_uid])
                gform_job = generate_gform_quiz.delay(class_quiz_id, teacher_uid)
                script_id = gform_job.get()
                #script_execution_job = execute_app_script.apply_async(args=[script_id, teacher_uid])
                #published_url = script_execution_job.get()
                #print("Publised URL: {}", published_url)
                # send_google_form_email.apply_async(args=[teacher["email"], published_url])
            except Exception as e:
                api_logger.exception(e)
                error_object["message"] = "Error generating Google Form"
                return make_response(error_object, 500)
            return make_response(jsonify({
                'status': 'Success',
                'message': 'Generated quiz!',
                'ScriptId': script_id
            }), 200)
        else:
            return make_response(jsonify(error_object), 400)

api.add_resource(ClassQuizPing, '/class_quiz/ping')
api.add_resource(ClassQuiz, '/class_quiz/<int:class_quiz_id>')
api.add_resource(ClassQuizGenerator, '/class_quiz/<int:class_quiz_id>/generate')
api.add_resource(ClassQuizGeneratorExecutor, '/class_quiz/<int:class_quiz_id>/<script_id>/generate/execute')
api.add_resource(ClassQuizList, '/class_quiz')
