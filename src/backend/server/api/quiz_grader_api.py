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

quiz_grader_blueprint = Blueprint('quiz_grader', __name__)
api = Api(quiz_grader_blueprint)

class QuizGradeCollector(Resource):
    def post(self):
        post_data = request.get_json()
        print(post_data)
        return 200


api.add_resource(QuizGradeCollector, '/grader')
