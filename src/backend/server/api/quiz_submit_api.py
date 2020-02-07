from flask import make_response, jsonify, Blueprint
from flask_restful import Resource, Api
import json

quiz_submit_blueprint = Blueprint('quiz_submit', __name__)
api = Api(quiz_submit_blueprint)

class SubmitQuiz(Resource):
    def post(self, quiz_payload):
        pass

api.add_resource(SubmitQuiz, '/submit_quiz')
