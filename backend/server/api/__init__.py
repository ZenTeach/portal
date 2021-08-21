import logging

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


@root_api.route("/subjects", methods=['GET'])
def subjects():
    from server.models import Subject, SubjectSchema
    dumper = SubjectSchema()
    subjects = Subject.query.all()

    response = [dumper.dump(subject) for subject in subjects]
    return make_response(jsonify({
        'subjects': response
    }), 200)
