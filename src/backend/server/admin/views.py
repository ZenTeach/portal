import json
from datetime import datetime

from flask_admin.contrib.sqla import ModelView
from flask_admin.model import typefmt
from jinja2 import Markup
from wtforms import SelectField

from server.models import QuestionTypeEnum


class BaseView(ModelView):
    can_export = True
    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'


def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup('<pre>{}</pre>'.format(json_value))

# TODO: Add unique key constraints on teacher, student, questions
# TODO: Add date formatting for teacher and student dob
# def date_formatter(view, context, model, name):
#     value = getattr(model, name)
#     return datetime.fromisoformat(value).

class QuestionView(BaseView):
    column_exclude_list = ['search_vector', 'uuid']
    column_filters = ('topic', 'question_type', 'subject', 'knowledge_item')
    column_formatters = {
        'choices': json_formatter,
    }
    form_excluded_columns = ['uuid']

    def scaffold_form(self):
        form = super().scaffold_form()
        form.question_type = SelectField(u'Question Type', choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('short_answer', 'Short Answer'),
            ('long_answer', 'Long Answer')
        ])
        form.subject = SelectField(u'Subject', choices=[
            ('chemistry', 'Chemistry'),
            ('biology', 'Biology'),
            ('physics', 'Physics')
        ])
        return form


class SchoolClassView(BaseView):
    column_exclude_list = ['uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes']

class StudentView(BaseView):
    column_exclude_list = ['password', 'role', 'uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'role']

class TeacherView(BaseView):
    column_exclude_list = ['password', 'role', 'uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'role']


class ClassQuizView(BaseView):
    column_exclude_list = ['uuid', 'questions', 'script_id', 'gform_id']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'created_at', 'school_class', 'student']
