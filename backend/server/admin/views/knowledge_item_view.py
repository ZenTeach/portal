from flask import flash

from .base_view import BaseView, logger, report_5xx_error


class KnowledgeItemView(BaseView):
    can_create = True
    can_edit = True
    can_export = False
    column_list = ["value", "linked_question_count"]
    column_exclude_list = ["id"]
    column_filters = ("value",)
    column_editable_list = ["value"]

    def delete_model(self, model):

        if model.linked_question_count > 0:
            flash("Cannot delete knowledge item as it has linked questions", "error")
            return
        try:
            model.delete()
            flash("Successfully deleted knowledge item", "success")
        except Exception as e:
            report_5xx_error(e)
            logger.error("Failed to delete record: {}".format(str(e)))
            flash("Failed to delete record: {}".format(str(e)), "error")
