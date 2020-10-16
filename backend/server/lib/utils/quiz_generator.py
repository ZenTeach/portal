import logging
import os.path as path
from pathlib import Path

from jinja2 import Environment, FileSystemLoader
from server.models import ClassQuiz as ClassQuizModel
from weasyprint import CSS, HTML
from weasyprint.fonts import FontConfiguration

logger = logging.getLogger(__name__)


class QuizGenerator:
    def __init__(self, template_dir, template_name, output_dir, **kwargs):
        self.template_dir = template_dir
        self.template_name = template_name
        self.output_dir = output_dir
        self.output_file = ""

    @classmethod
    def check_directories(cls, directory):
        return Path(directory).exists()

    def generate(self, quiz_id):
        if not self.check_directories(self.template_dir):
            raise OSError(f"Directory {self.template_dir} doesn't exist")

        quiz = ClassQuizModel.query.filter_by(id=quiz_id).first()
        if not quiz:
            raise Exception("Quiz not found!")

        if not self.check_directories(self.output_dir):
            Path(self.output_dir).mkdir(parents=True)
        try:
            env = Environment(loader=FileSystemLoader(self.template_dir), autoescape=True)
            template = env.get_template(self.template_name)
            template_vars = {
                "title": "{} quiz".format(quiz.subject),
                "subject": quiz.subject,
                "questions": quiz.questions,
            }
            html_out = template.render(template_vars)
            font_config = FontConfiguration()
            css = CSS(
                string="""
                @font-face {
                    font-family: 'Open Sans', Helvetica;
                    src: url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');  # noqa
                }
                h1 { font-family: 'Open Sans', Helvetica, sans-serif }""",
                font_config=font_config,
            )
            self.output_file = path.join(
                self.output_dir, "Quiz {}.pdf".format(quiz.id))
            HTML(string=html_out).write_pdf(
                self.output_file, stylesheets=[css], font_config=font_config
            )
        except Exception as e:
            logger.error(e)
            raise

    @property
    def quiz_file_name(self):
        return self.output_file
