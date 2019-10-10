from flask import Blueprint, current_app, jsonify, url_for, request, make_response
from server.models import Questions
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration

root_api = Blueprint('root', __name__)


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


@root_api.route("/demo_pdf")
def demo_pdf():
    all_chemistry_questions = Questions.query.filter_by(
        subject='Chemistry').all()
    env = Environment(loader=FileSystemLoader(
        '/home/flask/server/server/api/templates'))
    # import pdb
    # pdb.set_trace()
    template = env.get_template("demo.html")
    template_vars = {
        "title": "Demo chemistry quiz",
        "subject": "Chemistry",
        "questions": all_chemistry_questions
    }
    html_out = template.render(template_vars)
    font_config = FontConfiguration()
    css = CSS(string='''
        @font-face {
            font-family: 'Open Sans', Helvetica;
            src: url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');
        }
    h1 { font-family: 'Open Sans', Helvetica, sans-serif }''', font_config=font_config)
    HTML(string=html_out).write_pdf("/home/flask/server/server/api/tmp/quiz.pdf", stylesheets=[css],
                                    font_config=font_config)
    return make_response({
        'message': 'PDF generated'
    }, 200)
