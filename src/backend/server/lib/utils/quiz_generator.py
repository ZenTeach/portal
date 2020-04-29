import os.path as path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from pathlib import Path
from server.models import ClassQuiz as ClassQuizModel

class QuizGenerator():
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
            raise OSError("Directories don't exist")

        quiz = ClassQuizModel.query.filter_by(id=quiz_id).first()
        if not quiz:
            raise Exception("Quiz not found!")

        if not self.check_directories(self.output_dir):
            Path(self.output_dir).mkdir(parents=True)
        try:
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template(self.template_name)
            # TODO: change template vars
            template_vars = {
                "title": "Demo Chemistry quiz",
                "subject": "Chemistry",
                "questions": quiz.questions
            }
            html_out = template.render(template_vars)
            font_config = FontConfiguration()
            css = CSS(string='''
                @font-face {
                    font-family: 'Open Sans', Helvetica;
                    src: url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');
                }
                h1 { font-family: 'Open Sans', Helvetica, sans-serif }''', font_config=font_config)
            self.output_file = path.join(self.output_dir, "Quiz {}.pdf".format(quiz.id))
            HTML(string=html_out).write_pdf(self.output_file, stylesheets=[css],
                                    font_config=font_config)
        except Exception as e:
            print(e)

    @property
    def quiz_file_name(self):
        return self.output_file
