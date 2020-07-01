from flask import Blueprint, jsonify, make_response
from flask_jwt_extended import jwt_required
from flask_restful import Api, Resource
from server.decorators import with_required_roles

# from server.models import SchoolClass as SchoolClassModel


statistics_view_blueprint = Blueprint("stats", __name__)
api = Api(statistics_view_blueprint)


def correct_response_distribution_sql(student_id):
    return """
        SELECT * FROM class_quiz_scores WHERE student_id
    """


class StatsPing(Resource):
    def get(self):
        return make_response(
            jsonify({
                "status": "success",
                "message": "Pinged the stats api"
            }),
            200)


class StatsCorrectResponse(Resource):
    @jwt_required
    @with_required_roles(["Admin", "Teacher"])
    def get(self):
        """
            Returns a list of labels and
            results grouped by question
        """
        # identity = get_jwt_identity()["identity"]
        pass


api.add_resource(StatsPing, "/stats/ping")
api.add_resource(StatsCorrectResponse, "/stats/correct_response")
