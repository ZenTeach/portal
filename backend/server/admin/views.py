import json
import logging
import os
import re
from functools import lru_cache, reduce
from html import escape
from typing import List

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
from server import bcrypt
from server.config import _load_examboard
from server.models import Admin, QuestionChoice, Questions, Student, Teacher
from wtforms import (BooleanField, IntegerField, SelectField, StringField,
                     TextField, fields, form, validators)
from wtforms.compat import text_type
from wtforms.meta import DefaultMeta
from wtforms.widgets import HTMLString, TextInput, html_params

logger = logging.getLogger('admin::view')


def report_5xx_error(exception: Exception):
    sentry_dsn_key = os.environ.get("SENTRY_DSN")
    from sentry_sdk import init, capture_exception
    init(sentry_dsn_key)
    capture_exception(exception)


@lru_cache(64)
def _loaded_examboard() -> List:
    return list(_load_examboard().get('exam_board').items())


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

    def validate(self):
        return self.validate_login()

    def validate_login(self):
        user = self.get_user()

        if user is None:
            self.email.errors = "User not found"
            return False
        # we're comparing the plaintext pw with the the hash from the sdb
        if not bcrypt.check_password_hash(user.password, self.password.data.encode('utf-8')):
            self.password.errors = "Incorrect password"
            return False

        logger.info('Password accepted')

        return True

    def get_user(self):
        return Admin.query.filter_by(email=self.email.data).first()


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


class QuestionView(BaseView):
    column_exclude_list = ["search_vector", "uuid", "image_url"]
    column_filters = ("topic", "question_type", "subject", "knowledge_item", "user_created")
    column_formatters = {
        "choices": json_formatter,
        "correct_choice_id": correct_choice_formatter,
    }
    create_template = "admin/question_create.html"
    edit_template = "admin/question_edit.html"
    form_overrides = {"subject": SelectField,
                      "question_type": SelectField, 'exam_board': SelectField}
    form_create_rules = ('subject',
                         'exam_board',
                         'topic',
                         'knowledge_item',
                         'tag',
                         'question_type',
                         'question',
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
        'exam_board': dict(
            choices=_loaded_examboard()
        )
    }

    form_excluded_columns = ["uuid", "choices", "image_url",
                             "correct_choice", "correct_choice_id", "user_created"]

    # form_extra_fields = {
    #     'image_url': CustomImageUploadField('Image')
    # }

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
            data = form.data.copy()
            data.update(user_created=False)
            Questions.create_from_admin_form(data)
            return redirect(url_for("admin.question.index_view"))
        except Exception as e:
            report_5xx_error(e)
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


def exam_board_formatter(view, context, model, name):
    value = getattr(model, name)
    boards = _loaded_examboard()
    human_readable_value = boards.get(value)
    return human_readable_value


class SchoolClassView(BaseView):
    column_exclude_list = ["uuid"]
    form_excluded_columns = [
        "uuid", "student_attended_classes", "students", "quizzes"]

    column_formatters = {
        'exam_board': exam_board_formatter
    }
    boards = [(k, v) for k, v in dict(_loaded_examboard()).items()]
    form_overrides = {"subject": SelectField, "year_group": SelectField, 'exam_board': SelectField}
    form_args = {
        "subject": dict(
            choices=[
                ("chemistry", "Chemistry"),
                ("biology", "Biology"),
                ("physics", "Physics"),
            ]
        ),
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


class StudentView(BaseView):
    column_exclude_list = [
        "password",
        "role",
        "uuid",
        "password",
        "confirmed_at",
        "confirmation_token"
    ]
    form_excluded_columns = [
        "uuid",
        "student_attended_classes",
        "role",
        "quiz_sessions",
        "quiz_session",
        "quiz_grades",
        "quiz_grade",
        "password",
        "confirmed",
        "confirmed_at",
        "confirmation_token"
    ]
    column_formatters = {"date_of_birth": date_format}

    def create_model(self, form):
        try:
            instance = Student(
                form.data["firstname"],
                form.data["lastname"],
                form.data["email"]
            )

            instance.save()
            instance.add_from_class_list(form.data["classes"])
            return redirect(url_for("admin.student.index_view"))
        except Exception as e:
            report_5xx_error(e)
            flash("Failed to create record: {}".format(str(e)), "error")

    def delete_model(self, model):
        try:
            Student.remove_model(model)
            flash("Successfully deleted student", "success")
        except Exception as e:
            report_5xx_error(e)
            logger.error("Failed to delete record: {}".format(str(e)))
            flash("Failed to delete record: {}".format(str(e)), "error")


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
            report_5xx_error(e)
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


class SubjectsView(BaseView):
    can_create = False
    can_edit = True
    column_exclude_list = ["id"]
    form_excluded_columns = ["name"]
    column_filters = ("enabled",)
