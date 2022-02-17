
from flask import Blueprint, jsonify, make_response
from flask.views import MethodView
from flask_jwt_extended import current_user, jwt_required
from server.models import ActivityLogSchema

activity_log_blueprint = Blueprint("activity_log", __name__)
schema_dumper = ActivityLogSchema()


class ActivityLog(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        teacher = current_user
        activity_logs = teacher.activity_logs.limit(10)
        return make_response(
            jsonify(
                schema_dumper.dump(activity_logs, many=True)
            ), 200)


activity_log_blueprint.add_url_rule(
    "/activity_logs", view_func=ActivityLog.as_view('activitylog'))
