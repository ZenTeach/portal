"""
Shows basic usage of the Apps Script API.
Call the Apps Script API to create a new script project, upload a file to the
project, and log the script's URL to the user.
"""

from __future__ import print_function
import pickle
from pathlib import Path
import json
from jinja2 import Environment, FileSystemLoader
from server.models import ClassQuiz as ClassQuizModel

class GoogleFormsGenerator(object):
    def __init__(self, template_dir, quiz_id, js_tmpl):
        """
            Args:
                template_dir: Template directory
                js_tmpl: Javascript template file
                credentials: A credentials json file
                output_file: Pickle serialized output file location
                manifest_file: The manifest file directory
        """
        self.template_dir = template_dir
        self.quiz_id = quiz_id
        self.js_tmpl = js_tmpl
        self.quiz = None

    @classmethod
    def check_directories(self, directory):
        return Path(directory).exists()

    @property
    def current_quiz(self):
        return self.quiz

    def generate(self):
        if not self.check_directories(self.template_dir):
            raise OSError("Directories don't exist")

        self.quiz = ClassQuizModel.query.filter_by(id=self.quiz_id).first()

        if not self.quiz:
            raise Exception("Quiz not found!")

        try:
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template(self.js_tmpl)

            template_vars = {
                "subject": "Chemistry",
                "questions": self.quiz.questions
            }

            return template.render(template_vars)
        except Exception as e:
            print (e)

    def update_quiz(self, pr_id, dep_id, version_number):
        self.quiz.update_gform_id(pr_id, dep_id, version_number)
