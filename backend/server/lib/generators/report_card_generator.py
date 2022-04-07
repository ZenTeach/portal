import logging
import os.path as path
from json import decoder, loads
from pathlib import Path
from typing import List, Union
from uuid import UUID

from delta.html import render
from jinja2 import Environment, FileSystemLoader
from server.models import QuizGrade
from weasyprint import CSS, HTML
from weasyprint.text.fonts import FontConfiguration

logger = logging.getLogger(__name__)


def highlight_progress(progress_value: str) -> str:
    parsed = [int(x) for x in progress_value.split("/")]
    nom, denom = parsed

    if (nom > denom or denom == 0):
        return ''

    if (nom == 0):
        return 'red'
    elif (nom == denom):
        return 'green'
    else:
        return 'yellow'


def parse_json_blob(feedback_value: str) -> Union[dict, str]:
    try:
        return loads(feedback_value)
    except decoder.JSONDecodeError:
        return feedback_value


def render_quill_delta(parsed_data: Union[List[dict], str]) -> str:
    if type(parsed_data) == list and type(parsed_data[0]) == dict:
        return render(parsed_data, method='text')
    else:
        return parsed_data


class ModelNotFound(Exception):
    pass


class ReportCardGenerator(object):
    def __init__(self, template_dir, template_name, output_dir):
        self.template_dir = template_dir
        self.template_name = template_name
        self.output_dir = output_dir
        self.output_file = ""

    @classmethod
    def check_directories(cls, directory):
        return Path(directory).exists()

    def generate(self, grade_id: UUID):
        if not self.check_directories(self.template_dir):
            raise OSError(f"Directory {self.template_dir} doesn't exist")

        grade = QuizGrade.query.filter_by(uuid=grade_id, graded=True).first()
        if not grade:
            raise ModelNotFound("Graded Quiz not found!")

        if not self.check_directories(self.output_dir):
            Path(self.output_dir).mkdir(parents=True)

        try:
            env = Environment(
                loader=FileSystemLoader(self.template_dir),
                autoescape=True
            )

            env.globals.update(
                {
                    'highlight_progress': highlight_progress,
                    'render_quill_delta': render_quill_delta,
                    'enumerate': enumerate,
                    'json_loads': parse_json_blob
                })

            template = env.get_template(self.template_name)
            template_vars = {
                "reports": grade.grade_breakdown,
                "student_name": grade.student.full_name,
                "quiz_name": grade.class_quiz.name
            }
            html_out = template.render(template_vars)
            font_config = FontConfiguration()
            css = CSS(
                string="""
                @font-face {
                    font-family: 'Open Sans', Helvetica;
                    src: url('https://fonts.googleapis.com/css?family=Open+Sans&display=swap');  # noqa
                }
                body, h1 { font-family: 'Open Sans', Helvetica, sans-serif }
                table, caption, tbody, tfoot, thead, tr, th, td {
                    margin: 0;
                    padding: 0;
                    border: 0;
                    font-size: 100%;
                    font: inherit;
                    vertical-align: baseline;
                }
                table  {
                    border-collapse:collapse;
                    border-spacing:0;
                }
                table td {
                    font-family:Arial, sans-serif;
                    font-size:14px;
                    padding:10px 5px;
                    border-style:solid;
                    border-width:1px;
                    overflow:hidden;
                    word-break:normal;
                    border-color:black;
                }

                table th {
                    font-family:Arial, sans-serif;
                    font-size:12px;
                    font-weight:normal;
                    padding:10px 5px;
                    border-style:solid;
                    border-width:1px;
                    overflow:hidden;
                    word-break:normal;
                    border-color:black;
                }
                .red { color: black; background-color: #F44336; }
                .green { color: black; background-color: #4CAF50; }
                .yellow { color: black; #FFEB3B; }
                .tg .tg-cly1{text-align:left;vertical-align:middle}
                """,
                font_config=font_config,
            )
            self.output_file = path.join(
                self.output_dir, "Report_card_{}.pdf".format(grade.uuid))
            HTML(string=html_out).write_pdf(
                self.output_file, stylesheets=[css], font_config=font_config
            )
        except Exception as e:
            logger.error(e)
            raise

    @property
    def report_file_name(self):
        return self.output_file
