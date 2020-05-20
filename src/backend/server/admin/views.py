import json
from datetime import datetime, timedelta
from secrets import token_bytes, token_urlsafe

import flask_admin as admin
from flask import flash, redirect, request, session, url_for
from flask_admin.actions import action
from flask_admin.contrib.sqla import ModelView, ajax
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import BaseForm, Select2Field, Select2TagsField
from flask_admin.model import typefmt
from flask_login import current_user, login_user, logout_user
from jinja2 import Markup
from werkzeug.security import check_password_hash, generate_password_hash
from wtforms import SelectField, fields, form, validators, StringField, BooleanField, IntegerField
from wtforms.csrf.session import SessionCSRF
from wtforms.meta import DefaultMeta

from server import db as sdb
from server.models import Admin, Questions, QuestionTypeEnum, QuestionChoice, ChoiceFeedback

from flask_admin.form import RenderTemplateWidget
from flask_admin.model.form import InlineFormAdmin
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.contrib.sqla.fields import InlineModelFormList
from markupsafe import Markup
from flask_admin.model.fields import AjaxSelectField

class SecureForm(BaseForm):
    class Meta(DefaultMeta):
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = token_bytes()
        csrf_time_limit = timedelta(minutes=20)

        @property
        def csrf_context(self):
            return session

class BaseView(ModelView):
    can_export = True
    list_template = 'admin/list.html'
    create_template = 'admin/create.html'
    edit_template = 'admin/edit.html'
    form_base_class = SecureForm

    def is_accessible(self):
        return current_user.is_authenticated

def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup('<pre>{}</pre>'.format(json_value))

def date_format(view, context, model, name):
    value = getattr(model, name)
    return value.strftime('%Y-%m-%d')

class LoginForm(form.Form):
    email = fields.StringField(validators=[validators.required()], render_kw={"placeholder": "email"})
    password = fields.PasswordField(validators=[validators.required()], render_kw={"placeholder": "password"})

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


class QuestionChoiceForm(form.Form):
    value = StringField("Choice value", validators=[validators.InputRequired()])
    is_correct = BooleanField("Mark as correct")
    feedback = StringField("Choice Feedback", validators=[validators.DataRequired()])
    weight = IntegerField("Choice weight")

    def populate_obj(self, obj):
        pass

# This widget uses custom template for inline field list
class CustomInlineFieldListWidget(RenderTemplateWidget):
    def __init__(self):
        super(CustomInlineFieldListWidget, self).__init__('admin/field_list.html')


# This InlineModelFormList will use our custom widget and hide row controls
class CustomInlineModelFormList(InlineModelFormList):
    widget = CustomInlineFieldListWidget()

    def display_row_controls(self, field):
        return False

class CustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList

# Customized inline form handler
class QuestionChoiceInlineModelForm(InlineFormAdmin):
    form = QuestionChoiceForm
    form_excluded_columns = ('question_id', 'uuid', 'question')
    form_label = 'Choice'

    def __init__(self):
        super(QuestionChoiceInlineModelForm, self).__init__(QuestionChoice)

    def postprocess_form(self, form_class):
        form_class.value = StringField('value')
        return form_class

    def get_create_form(self):
        return QuestionChoiceForm

def correct_choice_formatter(view, context, model, name):
    value = getattr(model, name)
    return QuestionChoice.query.filter_by(uuid=value).first().value

class QuestionForm(form.Form):
    question = StringField("Question")
        # question_type = SelectField("Question Type", choices=[])
    question_type = SelectField(u'Question Type', choices=[
            ('multiple_choice', 'Multiple Choice'),
            ('short_answer', 'Short Answer'),
            ('long_answer', 'Long Answer')
        ])
    subject = SelectField(u'Subject', choices=[
            ('chemistry', 'Chemistry'),
            ('biology', 'Biology'),
            ('physics', 'Physics')
        ])
    topic = StringField("Topic")
    tag = StringField("Tag")
    knowledge_item = StringField("Knowledge Item")

class QuestionView(BaseView):
    form = QuestionForm
    column_exclude_list = ['search_vector', 'uuid']
    column_filters = ('topic', 'question_type', 'subject', 'knowledge_item')
    column_formatters = {
        'choices': json_formatter,
        'correct_choice': correct_choice_formatter
    }
    form_excluded_columns = ['uuid', 'choices', 'correct_choice']
    detail_modal = True
    inline_model_form_converter = CustomInlineModelConverter
    inline_models = (QuestionChoiceInlineModelForm(),)

    def edit_form(self, obj):
        import pdb; pdb.set_trace()
        edit_form = super().edit_form(obj=obj)
        edit_form.correct_choice = None

    # def scaffold_form(self):
    #     form = super().scaffold_form()
    #     return form

    @action('create_quiz', 'Create Quiz', 'Are you sure you want to create a quiz with the questions?')
    def action_approve(self, ids):
        try:
            # Given ids of questions,
            # Create quiz
            print(ids)

            flash("Success")
        except Exception as ex:
            if not self.handle_view_exception(ex):
                raise
            flash("Failed to create quiz.")

class SchoolClassView(BaseView):
    column_exclude_list = ['uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'students', 'quizzes']

class StudentView(BaseView):
    column_exclude_list = ['password', 'role', 'uuid' ]
    form_excluded_columns = ['uuid', 'student_attended_classes', 'role', 'quiz_sessions', 'quiz_session', 'quiz_grades', 'quiz_grade']
    column_formatters = {
        'date_of_birth': date_format
    }

# TODO: remove password field from edit form
class TeacherView(BaseView):
    column_exclude_list = ['password', 'role', 'uuid']
    form_excluded_columns = ['uuid', 'student_attended_classes', 'role']
    column_formatters = {
        'date_of_birth': date_format
    }

class ClassQuizView(BaseView):
    column_exclude_list = ['uuid', 'questions', 'script_id', 'gform_id', 'school_class']
    form_excluded_columns = ['uuid', 'status', 'held_on',
            'student_attended_classes', 'created_at',
            'student', 'gform_id', 'script_id',
            'student_quiz_sessions', 'student_quiz_grades',
            'quiz_session', 'student_quiz_grade']
