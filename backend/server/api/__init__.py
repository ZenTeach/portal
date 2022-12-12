import logging

from flask import Blueprint, current_app, jsonify
from flask.helpers import make_response
from server.models import (ActivityLog, Setting, SettingSchema, Subject,
                           SubjectSchema)

root_api = Blueprint("root", __name__)

if current_app:
    logger = current_app.logger
else:
    logger = logging.getLogger(__name__)


def log_activity(user, action, item_type, item_id, attributes={}, note=None):
    if (current_app.config.get('LOG_ACTIVITY')):
        ActivityLog.log(
            user,
            action,
            item_type,
            item_id,
            attributes,
            note
        )


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@root_api.route("/subjects", methods=['GET'])
def subjects():
    """
    ---
    get:
        description: Returns enabled subject
        responses:
            200:
                description: Return subjects
                content:
                    application/json:
                        schema: SubjectSchema

    """
    dumper = SubjectSchema()
    subjects = Subject.query.all()

    response = [dumper.dump(subject) for subject in subjects]
    return make_response(jsonify({
        'subjects': response
    }), 200)


@root_api.route("/settings", methods=['GET'])
def settings():
    """
    ---
    get:
        description: Returns app settings
        responses:
            200:
                description: Return app settings
                content:
                    application/json:
                        schema: SettingSchema
    """
    dumper = SettingSchema()
    setting = Setting()
    return make_response(jsonify(dumper.dump(setting)), 200)
