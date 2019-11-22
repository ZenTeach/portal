from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from pathlib import Path

class QuizGenerator():
    def __init__(self, template_dir, template_name, output_dir, **kwargs):
        self.template_dir = template_dir
        self.template_name = template_name
        self.output_dir = output_dir
        self.output_file = ""
        self.title = kwargs["title"]

    @classmethod
    def check_directories(self, directory):
        return Path(directory).exists()

    def generator(self, quiz):
        if not self.check_directories(self.template_dir) or not self.check_directories(output_dir):
            raise OSError("Directories don't exist")
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
            self.output_file = self.output_dir + "/{}.pdf".format("Quiz" + quiz.id)
            HTML(string=html_out).write_pdf(output_file, stylesheets=[css],
                                    font_config=font_config)
        except Exception as e:
            pass

    @property
    def quiz_file_name(self):
        return self.output_file
