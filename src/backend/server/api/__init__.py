import logging
from flask import Blueprint, current_app, jsonify, url_for, request, make_response
from server.models import Questions
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

root_api = Blueprint('root', __name__)

api_logger = logging.getLogger(__name__)


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
    return(jsonify(links))

@root_api.route("/ping")
def ping():
    return "pong", 200

# TODO: Use this to dynamically register api blueprint during app creation
# def register_blueprints(app):
#     """Automagically register all blueprint packages
#     Just take a look in the blueprints directory.
#     """
#     for name in find_modules('blueprints', recursive=True):
#         mod = import_string(name)
#         if hasattr(mod, 'bp'):
#             app.register_blueprint(mod.bp)
#     return None
