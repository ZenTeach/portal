import re
from functools import reduce
from html import escape

from flask import flash, redirect, url_for
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import ImageUploadField, RenderTemplateWidget
from flask_admin.model.form import InlineFormAdmin
from jinja2 import Markup
from server.models import QuestionChoice, Questions, Subject
from wtforms import (BooleanField, IntegerField, SelectField, StringField,
                     TextField)
from wtforms.compat import text_type
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.form import Form
from wtforms.validators import (DataRequired, InputRequired, Required,
                                ValidationError)
from wtforms.widgets import HTMLString, TextInput, html_params

from .base_view import BaseView, _loaded_examboard, correct_choice_formatter


class QuestionChoiceForm(Form):
    value = StringField("Choice value", validators=[
                        InputRequired()])
    feedback = StringField("Choice Feedback", validators=[
                           DataRequired()])
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


def has_choice_for_multiple_choice_type(form_data):
    choices = form_data.get('choices')
    question_type = form_data.get('question_type')
    message = "Multiple Choice type question must have between 2 and 6 choices present."

    if question_type == 'multiple_choice' and len(choices) == 0:
        raise ValidationError(message)


def one_correct_choice_validator(form_data, field):
    message = "Please select exactly one correct choice"
    choices = form_data.get('choices')
    has_correct_choice = reduce(
        (lambda acc, val: acc + 1 if val['is_correct_choice'] else acc), choices, 0)

    if has_correct_choice != 1:
        raise ValidationError(message)


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
    can_create = False
    column_exclude_list = ["search_vector", "uuid", "image_url", "knowledge_item", "topic"]
    column_filters = ("topic", "question_type", "subject", "knowledge_item", "user_created")
    column_formatters = {
        "correct_choice_id": correct_choice_formatter,
    }
    column_list = ['question', 'question_type', 'subject',
                   '_knowledge_item', '_topic', 'user_created', 'teacher']
    create_template = "admin/question_create.html"
    edit_template = "admin/question_edit.html"
    form_overrides = {
        "question_type": SelectField,
        'exam_board': SelectField,
        "topic": SelectField,
        "knowledge_item": SelectField}
    form_create_rules = ('subject',
                         'exam_board',
                         'topic',
                         'knowledge_item',
                         'tag',
                         'question_type',
                         'question',
                         'choices')

    form_args = {
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

    def scaffold_form(self):
        form = super().scaffold_form()
        form.subject = QuerySelectField('Subject',
                                        validators=[Required()],
                                        query_factory=lambda: Subject.query.filter_by(
                                            enabled=True).all(),
                                        allow_blank=False)

        return form

    def create_form(self):
        form = super().create_form()
        # filter these values using the subject selected.
        # Prepopulate the choices with the subject selected.
        # form.knowledge_item = QuerySelectField('Knowledge Item',
        #                                         validators=[Required()],
        #                                         query_factory=lambda: KnowledgeItem.query.filter_by(  # noqa
        #                                             subject=form.subject.data
        #                                         ).all(),
        #                                         allow_blank=False)
        # form.topic = QuerySelectField('Topic',
        #                                 validators=[Required()],
        #                                 query_factory=lambda: Topic.query.filter_by(
        #                                     subject=form.subject.data
        #                                 ).all(),
        #                                 allow_blank=False)
        return form

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
            data.update(user_created=False, subject=str(data.get('subject')))
            Questions.create_from_admin_form(data)
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
