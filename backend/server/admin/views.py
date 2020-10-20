import json
import os
import re
from functools import reduce
from html import escape
from pathlib import Path

import flask_admin as admin
from flask import current_app, flash, redirect, request, session, url_for
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import ImageUploadField, RenderTemplateWidget, SecureForm
from flask_admin.model.form import InlineFormAdmin
from flask_login import current_user, login_user, logout_user
from flask_wtf.csrf import _FlaskFormCSRF
from jinja2 import Markup
from server import db as sdb
from server.models import Admin, QuestionChoice, Questions, Student, Teacher
from werkzeug.security import check_password_hash
from wtforms import (BooleanField, IntegerField, SelectField, StringField,
                     TextField, fields, form, validators)
from wtforms.compat import text_type
from wtforms.meta import DefaultMeta
from wtforms.widgets import HTMLString, TextInput, html_params


class CustomSecureForm(SecureForm):
    class Meta(DefaultMeta):
        csrf_class = _FlaskFormCSRF
        csrf_context = session

        @property
        def csrf_secret(self):
            return current_app.\
                config.\
                get("WTF_CSRF_SECRET_KEY",
                    current_app.secret_key)

        @property
        def csrf_time_limit(self):
            return current_app.config.get("WTF_CSRF_TIME_LIMIT", 3600)


class BaseView(ModelView):
    can_export = True
    list_template = "admin/list.html"
    create_template = "admin/create.html"
    edit_template = "admin/edit.html"
    form_base_class = CustomSecureForm

    def is_accessible(self):
        return current_user.is_authenticated


def json_formatter(view, context, model, name):
    value = getattr(model, name)
    json_value = json.dumps(value, ensure_ascii=False, indent=2)
    return Markup("<pre>{}</pre>".format(json_value))


def date_format(view, context, model, name):
    value = getattr(model, name)
    return value.strftime("%Y-%m-%d")


class LoginForm(form.Form):
    email = fields.StringField(
        validators=[validators.required()], render_kw={"placeholder": "email"}
    )
    password = fields.PasswordField(
        validators=[validators.required()],
        render_kw={"placeholder": "password"}
    )

    def validate_login(self, field):
        user = self.get_user()

        if user is None:
            raise validators.ValidationError("Invalid user")

        # we're comparing the plaintext pw with the the hash from the sdb
        if not check_password_hash(user.password, self.password.data):
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError("Invalid password")

    def get_user(self):
        return sdb.session.query(Admin).filter_by(email=self.email.data).first()


class ZenteachAdminIndexView(admin.AdminIndexView):
    @admin.expose("/")
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for(".login_view"))
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose("/login/", methods=("GET", "POST"))
    def login_view(self):
        form = LoginForm(request.form)
        if admin.helpers.validate_form_on_submit(form):
            user = form.get_user()
            login_user(user)

        if current_user.is_authenticated:
            return redirect(url_for(".index"))
        self._template_args["form"] = form
        return super(ZenteachAdminIndexView, self).index()

    @admin.expose("/logout/")
    def logout_view(self):
        logout_user()
        return redirect(url_for(".index"))


class QuestionChoiceForm(form.Form):
    value = StringField("Choice value", validators=[
                        validators.InputRequired()])
    feedback = StringField("Choice Feedback", validators=[
                           validators.DataRequired()])
    weight = IntegerField("Choice weight")
    is_correct_choice = BooleanField("Is this the correct choice?")


class CustomInlineFieldListWidget(RenderTemplateWidget):
    def __init__(self):
        super(CustomInlineFieldListWidget, self).__init__(
            "admin/field_list.html")


class CustomInlineModelFormList(InlineModelFormList):
    widget = CustomInlineFieldListWidget()

    def display_row_controls(self, field):
        return True


class CustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList


class CKTextAreaWidget(TextInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        return HTMLString('<div> \
                            <input type="hidden" {html_params}/>\
                            <div class="editor" {html_params}>\
                                <p>{escaped_content}</p>\
                            </div>\
                          </div>'.format(
            html_params=html_params(name=field.id, **kwargs),
            escaped_content=escape(text_type(field._value()), quote=False)
        ))


class CKTextAreaField(TextField):
    widget = CKTextAreaWidget()


class QuestionChoiceInlineModelForm(InlineFormAdmin):
    form_excluded_columns = ("question_id", "uuid", "question")
    form_label = "Choices"
    form_overrides = {
        'feedback': CKTextAreaField
    }

    def __init__(self):
        super(QuestionChoiceInlineModelForm, self).__init__(QuestionChoice)

    def postprocess_form(self, form_class):
        form_class.is_correct_choice = BooleanField(
            "Is this the correct choice?")
        return form_class


def correct_choice_formatter(view, context, model, name):
    value = getattr(model, name)
    choice = QuestionChoice.query.filter_by(id=value).first()
    if choice:
        return choice.value
    else:
        return ""


def has_choice_for_multiple_choice_type(form_data):
    choices = form_data.get('choices')
    question_type = form_data.get('question_type')
    message = "Multiple Choice type question must have between 2 and 6 choices present."

    if question_type == 'multiple_choice' and len(choices) == 0:
        raise validators.ValidationError(message)


def one_correct_choice_validator(form_data, field):
    message = "Please select exactly one correct choice"
    choices = form_data.get('choices')
    has_correct_choice = reduce(
        (lambda acc, val: acc + 1 if val['is_correct_choice'] else acc), choices, 0)

    if has_correct_choice != 1:
        raise validators.ValidationError(message)


def selected_correct_choice(form_data, field):
    return [int(x["id"]) for x in form_data["choices"] if x.get(field) == True][0]  # noqa


class CustomImageUploadInputWidget(object):
    empty_template = ('<input %(file)s>')

    data_template = ('<div class="image-thumbnail">'
                     ' <img %(image)s>'
                     ' <input type="checkbox" name="%(marker)s">Delete</input>'
                     ' <input %(text)s>'
                     '</div>'
                     '<input %(file)s>')

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.name)

        args = {
            'text': html_params(type='hidden',
                                value=field.data,
                                name=field.name),
            'file': html_params(type='file',
                                **kwargs),
            'marker': '_%s-delete' % field.name
        }

        url_re = r'^https:\/\/*'
        if field.data and isinstance(field.data, str):
            if re.match(url_re, field.data):
                url = field.data
            else:
                url = self.get_url(field)
            args['image'] = html_params(src=url)

            template = self.data_template
        else:
            template = self.empty_template

        return Markup(template % args)

    def get_local_url(self, data):
        pass


class CustomImageUploadField(ImageUploadField):
    widget = CustomImageUploadInputWidget()


file_path = str(Path(os.environ.get('TMP_DIR')).resolve())


class QuestionView(BaseView):
    column_exclude_list = ["search_vector", "uuid", "image_url"]
    column_filters = ("topic", "question_type", "subject", "knowledge_item")
    column_formatters = {
        "choices": json_formatter,
        "correct_choice_id": correct_choice_formatter,
    }
    create_template = "admin/question_create.html"
    edit_template = "admin/question_edit.html"
    form_overrides = {"subject": SelectField, "question_type": SelectField}
    form_create_rules = ('subject',
                         'topic',
                         'knowledge_item',
                         'tag',
                         'question_type',
                         'question',
                         'image_url',
                         'choices')

    form_args = {
        "subject": dict(
            choices=[
                ("chemistry", "Chemistry"),
                ("biology", "Biology"),
                ("physics", "Physics"),
            ]
        ),
        "question_type": dict(
            choices=[
                ("multiple_choice", "Multiple Choice"),
                ("short_answer", "Short Answer"),
                ("long_answer", "Long Answer"),
            ]
        ),
    }

    form_excluded_columns = ["uuid", "choices",
                             "correct_choice", "correct_choice_id"]

    form_extra_fields = {
        'image_url': CustomImageUploadField('Image')
    }

    detail_modal = True
    inline_model_form_converter = CustomInlineModelConverter
    inline_models = (QuestionChoiceInlineModelForm(),)

    def edit_form(self, obj):
        # handle correct question choice updates
        choice_id = obj.correct_choice_id
        for choice in obj.choices:
            if choice.id == choice_id:
                choice.is_correct_choice = True

        edit_form = super().edit_form(obj=obj)
        return edit_form

    def create_model(self, form):
        try:
            one_correct_choice_validator(form.data, "is_correct_choice")
            has_choice_for_multiple_choice_type(form.data)
            Questions.create_from_admin_form(form.data)
            return redirect(url_for("admin.question.index_view"))
        except Exception as e:
            flash("Failed to create record: {error}s".format(error=str(e)), "error")

    def on_model_change(self, form, model, is_created):
        if not is_created:  # Model updated
            _selected_correct_choice = selected_correct_choice(
                form.data, "is_correct_choice"
            )
            one_correct_choice_validator(form.data, "is_correct_choice")
            has_choice_for_multiple_choice_type(form.data)
            model.correct_choice_id = _selected_correct_choice
            model.save()
            return redirect(url_for("admin.question.index_view"))


class SchoolClassView(BaseView):
    column_exclude_list = ["uuid"]
    form_excluded_columns = [
        "uuid", "student_attended_classes", "students", "quizzes"]


class StudentView(BaseView):
    column_exclude_list = ["password", "role", "uuid", "password"]
    form_excluded_columns = [
        "uuid",
        "student_attended_classes",
        "role",
        "quiz_sessions",
        "quiz_session",
        "quiz_grades",
        "quiz_grade",
        "password",
    ]
    column_formatters = {"date_of_birth": date_format}

    def create_model(self, form):
        try:
            instance = Student(
                form.data["firstname"], form.data["lastname"], form.data["email"]
            )
            instance.save()
            return redirect(url_for("admin.student.index_view"))
        except Exception as e:
            flash("Failed to create record: {}".format(str(e)), "error")


class TeacherView(BaseView):
    column_exclude_list = ["password",
                           "role",
                           "uuid",
                           "confirmed",
                           "confirmed_at",
                           "confirmation_token",
                           "recovered_at",
                           "recovery_token"]

    form_excluded_columns = ["uuid",
                             "student_attended_classes",
                             "role",
                             "password",
                             "confirmed",
                             "confirmed_at",
                             "confirmation_token",
                             "recovered_at",
                             "recovery_token"]

    column_formatters = {"date_of_birth": date_format}

    def create_model(self, form):
        try:
            instance = Teacher(
                form.data["firstname"],
                form.data["lastname"],
                form.data["email"],
                form.data["date_of_birth"],
                form.data["classes"],
            )
            instance.save()
            return redirect(url_for("admin.teacher.index_view"))
        except Exception as e:
            flash("Failed to create record: {}".format(str(e)), "error")


class ClassQuizView(BaseView):
    can_create = False
    column_exclude_list = ["uuid", "questions",
                           "script_id", "gform_id", "school_class"]
    form_excluded_columns = [
        "uuid",
        "status",
        "held_on",
        "student_attended_classes",
        "created_at",
        "student",
        "gform_id",
        "script_id",
        "student_quiz_sessions",
        "student_quiz_grades",
        "quiz_session",
        "student_quiz_grade",
    ]


class UserInvitationView(BaseView):
    can_create = False
    can_edit = False
    column_exclude_list = ["invite_sent_at"]
