from flask import Flask, request, json, url_for
import glob
from flask_cors import CORS
import sys
import os
import sqlalchemy as db 
import zlib
import base64
# import pandas as pd

dirname = os.path.dirname(__file__)
app = Flask(__name__)
cors = CORS(app)

host = 'localhost'
port = '5432'
db_name = 'zenteachDB'
password = 'docker'

engine = db.create_engine(f'postgresql://postgres:{password}@{host}:{port}/{db_name}')
conn = engine.connect()

@app.route('/get_class')
def get_class():
    class_data = request.args.get('class_name')
    return (json.jsonify(class_data))

@app.route('/get_students')
def get_students():
        return {}
#     result = pd.read_sql_query("select * from zenteach.student", conn)
#     result = result.to_dict(orient='records')
#     print('result = ', result)
#     return (json.jsonify(result))

@app.route('/get_quiz')
def get_quiz():
    quiz_data = request.args.get('quiz_name')
    print('jsonified quiz_data = ', json.jsonify(quiz_data))
    return (json.jsonify(quiz_data))

### from stackoverflow ###
def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)

@app.route("/")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return(json.jsonify(links))