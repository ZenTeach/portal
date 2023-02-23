from flask import flash
# from flask_admin.contrib.sqla.fields import InlineFieldList
from server.models import Subject
# from wtforms.utils import unset_value
from wtforms.validators import DataRequired
from wtforms_alchemy.fields import QuerySelectField

from .base_view import BaseView, logger

# class InlineHstoreList(InlineFieldList):
#     def process(self, formdata, data=unset_value, extra_filters=None):
#         """ SQLAlchemy returns a dict for HSTORE columns, but WTForms cannot
#         process a dict. This overrides `process` to convert the dict
#         returned by SQLAlchemy to a list of classes before processing. """
#         if isinstance(data, dict):
#             data = [KeyValue(k, v) for k, v in iteritems(data)]
#         super(InlineHstoreList, self).process(formdata, data, extra_filters)


class TopicView(BaseView):
    can_create = True
    can_edit = True
    can_export = False
    column_list = ["value", "linked_question_count", "teacher", "subject"]
    column_exclude_list = ["id", "value_translations"]
    column_filters = ("value", "subject")
    column_editable_list = ["value"]
    # form_overrides = {
    #     "value_translations": InlineHstoreList
    # }

    def scaffold_form(self):
        form = super().scaffold_form()
        form.subject = QuerySelectField('Subject',
                                        validators=[DataRequired()],
                                        query_factory=lambda: Subject.query.filter_by(
                                            enabled=True).all())
        # form.value_translations = InlineHstoreList(
        #     'value_translations', validators=[DataRequired()])
        return form

    def edit_form(self, obj):
        form = super().edit_form(obj=obj)
        return form

    def delete_model(self, model):

        if model.linked_question_count > 0:
            flash("Cannot delete topic as it has linked questions", "error")
            return
        try:
            model.delete()
            flash("Successfully deleted topic", "success")
        except Exception as e:
            logger.error("Failed to delete record: {}".format(str(e)))
            flash("Failed to delete record: {}".format(str(e)), "error")
