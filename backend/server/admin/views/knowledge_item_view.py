from flask import flash, redirect, url_for
from server.models import Subject
from server.models.knowledge_item import KnowledgeItem
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from .base_view import BaseView, logger


class KnowledgeItemView(BaseView):
    can_create = True
    can_edit = True
    can_export = False
    column_list = ["value", "linked_question_count", "topic", "teacher"]
    column_exclude_list = ["id"]
    column_filters = ("value", "topic")
    column_editable_list = ["value"]

    def scaffold_form(self):
        form = super().scaffold_form()
        form.subject = QuerySelectField('Subject',
                                        validators=[Required()],
                                        query_factory=lambda: Subject.query.filter_by(
                                            enabled=True).all())
        return form

    def delete_model(self, model):

        if model.linked_question_count > 0:
            flash("Cannot delete knowledge item as it has linked questions", "error")
            return
        try:
            model.delete()
            flash("Successfully deleted knowledge item", "success")
        except Exception as e:
            logger.error("Failed to delete record: {}".format(str(e)))
            flash("Failed to delete record: {}".format(str(e)), "error")

    def create_model(self, form):
        try:
            data = form.data.copy()
            ki = KnowledgeItem(value=data.pop('value'))
            try:
                ki.topic = data.pop('topic', None)
                ki.subject = data.pop('subject', None)
                ki.questions = data.get('questions', [])
                ki.save()
            except Exception as e:
                flash(f"Error: {e}", "error")
        except Exception as e:
            logger.error("Failed to create record: {}".format(str(e)))
            flash("Failed to create record: {}".format(str(e)), "error")
        finally:
            return redirect(url_for("admin.question.index_view"))

    def on_model_change(self, form, model, is_created):
        if not is_created:
            try:
                data = form.data.copy()
                model.update_from_dict(data)
                model.save()
            except Exception as e:
                logger.error("Failed to update record: {}".format(str(e)))
                flash("Failed to update record: {}".format(str(e)), "error")
            finally:
                return redirect(url_for("admin.question.index_view"))
