import logging

from flask import Blueprint, current_app, jsonify
from flask.helpers import make_response
from flask_apispec import doc, marshal_with
from server import docs
from server.models import (ActivityLog, Setting, SettingSchema, Subject,
                           SubjectSchema)

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
@doc(description='Returns enabled subjects')
@marshal_with(SubjectSchema)
def subjects():
    dumper = SubjectSchema()
    subjects = Subject.query.all()

    response = [dumper.dump(subject) for subject in subjects]
    return make_response(jsonify({
        'subjects': response
    }), 200)


docs.register(subjects, endpoint='subjects', blueprint='root')


@root_api.route("/settings", methods=['GET'])
@marshal_with(SettingSchema)
def settings():
    dumper = SettingSchema()
    setting = Setting()
    return make_response(jsonify(dumper.dump(setting)), 200)


docs.register(settings, endpoint='settings', blueprint='root')
