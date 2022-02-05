import logging

from flask import Blueprint, current_app, jsonify
from flask.helpers import make_response
from server.models import ActivityLog

root_api = Blueprint("root", __name__)

if current_app:
    logger = current_app.logger
else:
    logger = logging.getLogger(__name__)


def log_activity(user, action, item_type, item_id, note=None):
    ActivityLog.log(
        user,
        action,
        item_type,
        item_id,
        note
    )


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@root_api.route("/subjects", methods=['GET'])
def subjects():
    from server.models import Subject, SubjectSchema
    dumper = SubjectSchema()
    subjects = Subject.query.all()

    response = [dumper.dump(subject) for subject in subjects]
    return make_response(jsonify({
        'subjects': response
    }), 200)


@root_api.route("/settings", methods=['GET'])
def settings():
    from server.models import Setting, SettingSchema

    dumper = SettingSchema()
    setting = Setting()
    return make_response(jsonify(dumper.dump(setting)), 200)
