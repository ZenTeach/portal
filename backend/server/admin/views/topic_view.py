from flask import flash
from server.models import Subject
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from .base_view import BaseView, logger


class TopicView(BaseView):
    can_create = True
    can_edit = True
    can_export = False
    column_list = ["value", "linked_question_count", "teacher", "subject"]
    column_exclude_list = ["id"]
    column_filters = ("value",)
    column_editable_list = ["value"]

    def scaffold_form(self):
        form = super().scaffold_form()
        form.subject = QuerySelectField('Subject',
                                        validators=[Required()],
                                        query_factory=lambda: Subject.query.filter_by(
                                            enabled=True).all(),
                                        allow_blank=False)
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
