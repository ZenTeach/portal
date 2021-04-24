import logging
import os

from flask import Blueprint, current_app, jsonify
from flask.helpers import make_response

root_api = Blueprint("root", __name__)

if current_app:
    logger = current_app.logger
else:
    logger = logging.getLogger(__name__)


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@root_api.errorhandler(500)
def root_api_exception_handler(e):
    report_5xx_error(e)
    return


def report_5xx_error(exception: Exception):
    sentry_dsn_key = os.environ.get("SENTRY_DSN")
    from sentry_sdk import init, capture_exception
    init(sentry_dsn_key)
    capture_exception(exception)


@root_api.route("/subjects", methods=['GET'])
def subjects():
    from server.models import Subject, SubjectSchema
    dumper = SubjectSchema()
    subjects = Subject.query.all()

    response = [dumper.dump(subject) for subject in subjects]
    return make_response(jsonify({
        'subjects': response
    }), 200)
