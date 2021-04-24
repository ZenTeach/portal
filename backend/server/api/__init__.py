import logging
import os

from flask import Blueprint, current_app, jsonify, url_for
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


@root_api.route("/")
def site_map():
    links = []
    for rule in current_app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return jsonify(links)


@root_api.errorhandler(500)
def root_api_exception_handler(e):
    report_5xx_error(e)
    return


@root_api.route("/ping")
def ping():
    return make_response("pong", 500)


def report_5xx_error(exception: Exception):
    sentry_dsn_key = os.environ.get("SENTRY_DSN")
    from sentry_sdk import init, capture_exception
    init(sentry_dsn_key)
    capture_exception(exception)
