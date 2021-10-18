import logging
import re
from functools import reduce
from html import escape
from io import BytesIO
from typing import List, Optional

from flask import flash, redirect, request, url_for
from flask_admin.base import expose
from flask_admin.contrib.sqla.fields import InlineModelFormList
from flask_admin.contrib.sqla.form import InlineModelConverter
from flask_admin.form import ImageUploadField, RenderTemplateWidget
from flask_admin.model.form import InlineFormAdmin
from jinja2 import Markup
from pandas import read_csv
from pandas.core.frame import DataFrame
from server.models import (KnowledgeItem, QuestionChoice, Questions, Subject,
                           Topic)
from server.models.questions import QuestionTypeEnum
from sqlalchemy import and_
from wtforms import (BooleanField, IntegerField, SelectField, StringField,
                     TextField)
from wtforms.compat import text_type
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.form import Form
from wtforms.validators import (DataRequired, InputRequired, Required,
                                ValidationError)
from wtforms.widgets import HTMLString, TextInput, html_params

from .base_view import BaseView, _loaded_examboard, correct_choice_formatter

logger = logging.getLogger('admin::view')


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
    can_import = True
    import_types = ['csv']
    column_exclude_list = ["search_vector", "uuid", "image_url", "knowledge_item", "topic"]
    column_filters = ("topic", "question_type", "subject", "knowledge_item", "user_created")
    column_formatters = {
        "correct_choice_id": correct_choice_formatter,
    }
    column_list = ['question', 'question_type', 'subject',
                   'knowledge_item', 'topic', 'user_created', 'teacher']
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
                                            enabled=True).all())
        form.topic = QuerySelectField('Topic',
                                      validators=[Required()],
                                      query_factory=lambda: Topic.query.all())
        form.knowledge_item = QuerySelectField('Knowledge Item',
                                               validators=[Required()],
                                               query_factory=lambda: KnowledgeItem.query.all())

        return form

    def create_form(self):
        form = super().scaffold_form()
        return form

    def edit_form(self, obj):
        # handle correct question choice updates
        choice_id = obj.correct_choice_id
        for choice in obj.choices:
            if choice.id == choice_id:
                choice.is_correct_choice = True

        logger.debug(obj)
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

    @property
    def validation_headers(self) -> List[str]:
        headers = [
            "Subject", "Topic", "Knowledge item", "Question", "Option A",
            "Option B", "Option C", "Option D", "Correct", "Tag", "Feedback A",
            "Feedback B", "Feedback C", "Feedback D"]
        return headers

    def _validate_file(self, io_stream: BytesIO) -> Optional[DataFrame]:
        headers = list(map(str.lower, self.validation_headers))
        headers.pop(headers.index('knowledge item'))
        headers.append('knowledge_item')
        io_stream.seek(0)
        data = read_csv(io_stream)
        data.dropna(how='all', axis=0, inplace=True)
        data.dropna(how='all', axis=1, inplace=True)
        data.fillna('', inplace=True)
        data.rename(str.lower, axis='columns', inplace=True)
        data.rename({'knowledge item': 'knowledge_item'}, axis='columns', inplace=True)
        data = data.filter(headers)
        return data.to_dict(orient='index')

    def _build_choices_hash(self, data: dict) -> List[dict]:
        """
            {
                'value': None,
                'feedback': None,
                'weight': None
            }
        """
        choices = []
        correct_answer = data.get('correct').lower()
        for i in ['a', 'b', 'c', 'd']:
            value = str(data.pop(f"option {i}"))
            feedback = str(data.pop(f"feedback {i}"))
            if value == '' or feedback == '':
                next
            choice_obj = {
                'value': value,
                'feedback': feedback,
                'weight': 0,
                'is_correct_choice': False,
            }
            if i == correct_answer:
                choice_obj.update({
                    'is_correct_choice': True,
                    'weight': 1
                })
                choices.append(choice_obj)
            else:
                choices.append(choice_obj)
        return choices

    def _import_csv(self, file_obj):
        try:
            validated_data = self._validate_file(file_obj)
        except Exception as e:
            flash(str(e), "error")
            return redirect(url_for('.index_view'))
        count = len(validated_data.keys())
        run_count = 0
        skip_count = 0
        str_fmt = "Imported {run_count}/{count} questions"
        for _index, val in validated_data.items():
            logger.debug(str_fmt.format(run_count=run_count, count=count))
            try:
                choices = self._build_choices_hash(val)
                val.update({
                    'choices': choices,
                    'question_type': QuestionTypeEnum.multiple_choice.name,
                    'exam_board': 'aqa',
                    'user_created': False
                })
                # look for duplicates
                unique_q_count = Questions.query\
                    .join(Questions.subject)\
                    .join(Questions.topic)\
                    .filter(and_(Subject.name == val['subject'],
                                 Topic.value == val['topic']))\
                    .filter(Questions.question == val['question']).count()
                if unique_q_count == 0:
                    Questions.create_from_admin_form(val)
                    run_count += 1
                else:
                    logger.debug("Found a question with {}, topic: {}, subject: {}".format(
                        val['question'], val['topic'], val['subject']))
                    skip_count += 1
            except Exception as e:
                logger.error(e)
                flash(str(e), "error")
                return redirect(url_for('.index_view'))
        msg = f"Imported {run_count} out of {count} questions. Found {skip_count} duplicates."
        flash(msg, "success")
        return redirect(url_for('.index_view'))

    @expose('/import/', methods=('POST',))
    def import_(self):
        upload_file = request.files['file']

        return self._import_csv(upload_file)
