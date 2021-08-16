from server.models import Subject
from wtforms import SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from .base_view import (BaseView, _loaded_examboard, exam_board_formatter,
                        subject_formatter)


class SchoolClassView(BaseView):
    column_exclude_list = ["uuid"]
    form_excluded_columns = [
        "uuid", "student_attended_classes", "students", "quizzes", "key_stage"]

    column_formatters = {
        'exam_board': exam_board_formatter,
        'subject': subject_formatter
    }
    boards = [(k, v) for k, v in dict(_loaded_examboard()).items()]
    form_overrides = {"year_group": SelectField, 'exam_board': SelectField}
    form_args = {
        "year_group": dict(
            choices=[
                ("Year 7", "Year 7"),
                ("Year 8", "Year 8"),
                ("Year 9", "Year 9"),
                ("Year 10", "Year 10"),
                ("Year 11", "Year 11"),
                ("Year 12", "Year 12"),
                ("Year 13", "Year 13")
            ]
        ),
        'exam_board': dict(
            choices=boards
        )
    }

    def scaffold_form(self):
        form = super().scaffold_form()
        form.subject = QuerySelectField('Subject',
                                        validators=[Required()],
                                        query_factory=lambda: Subject.query.filter_by(
                                            enabled=True).all(),
                                        allow_blank=False)
        return form
