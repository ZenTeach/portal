from flask import Blueprint, jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import jwt_required
from server.decorators import with_required_roles

statistics_view_blueprint = Blueprint("stats", __name__)


def correct_response_distribution_sql(student_id):
    return """
        SELECT * FROM class_quiz_scores WHERE student_id
    """


class StatsPing(MethodView):
    def get(self):
        return make_response(
            jsonify({
                "status": "success",
                "message": "Pinged the stats api"
            }),
            200)


class StatsCorrectResponse(MethodView):
    @jwt_required
    @with_required_roles(["Admin", "Teacher"])
    def get(self):
        """
            Returns a list of labels and
            results grouped by question
        """
        # identity = get_jwt_identity()["identity"]
        pass


statistics_view_blueprint.add_url_rule("/stats/ping", view_func=StatsPing.as_view('stats_ping'))
statistics_view_blueprint.add_url_rule(
    "/stats/correct_response", view_func=StatsCorrectResponse.as_view('stats_correct_response'))
