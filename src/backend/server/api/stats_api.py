from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Api, Resource
from server import db
from server.decorators import with_required_roles
# from server.models import SchoolClass as SchoolClassModel
from sqlalchemy import exc


statistics_view_blueprint = Blueprint('stats', __name__)
api = Api(statistics_view_blueprint)


class StatsPing(Resource):
    def get(self):
        return make_response('success', 200)


class StatsCorrectResponse(Resource):
    @jwt_required
    @with_required_roles(['Admin', 'Teacher'])
    def get(self):
        """
            Returns a list of labels and
            results grouped by question
        """
        identity = get_jwt_identity()['identity']


api.add_resource(StatsPing, '/stats/ping')
api.add_resource(StatsCorrectResponse, '/stats/correct_response')
