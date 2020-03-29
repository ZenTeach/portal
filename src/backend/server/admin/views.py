import json
from datetime import datetime

from flask_admin.contrib.sqla import ModelView
import flask_admin as admin
from flask import redirect, url_for, request
from flask_admin.model import typefmt
from flask_login import current_user, login_user, logout_user
from jinja2 import Markup
from wtforms import SelectField, form, fields, validators
from werkzeug.security import generate_password_hash, check_password_hash

from server.models import QuestionTypeEnum, Admin
from server import db as sdb

class BaseView(ModelView):
    can_export = True
    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'

    def is_accessible(self):
        return current_user.is_authenticated

def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup('<pre>{}</pre>'.format(json_value))

# TODO: Add unique key constraints on teacher, student, questions
def date_format(view, context, model, name):
    value = getattr(model, name)
    return value.strftime('%Y-%m-%d')

class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()])
    password = fields.PasswordField(validators=[validators.required()])

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the sdb
        if not check_password_hash(user.password, self.password.data):
        # to compare plain text passwords use
        # if user.password != self.password.data:
            raise validators.ValidationError('Invalid password')

    def get_user(self):
        return sdb.session.query(Admin).filter_by(email=self.email.data).first()


class ZenteachAdminIndexView(admin.AdminIndexView):
    @admin.expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        # handle user login
        form = LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for('.index'))
        link = '<p>Don\'t have an account? <a href="">Click here to register.</a></p>'
        self._template_args['form'] = form
        #self._template_args['link'] = link
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


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
    column_formatters = {
        'date_of_birth': date_format
    }

class TeacherView(BaseView):
    column_exclude_list = ['password', 'role', 'uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'role']
    column_formatters = {
        'date_of_birth': date_format
    }

class ClassQuizView(BaseView):
    column_exclude_list = ['uuid', 'questions', 'script_id', 'gform_id']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'created_at', 'school_class', 'student']
