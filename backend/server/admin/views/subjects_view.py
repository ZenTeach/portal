from .base_view import BaseView


class SubjectsView(BaseView):
    can_create = False
    can_edit = True
    column_exclude_list = ["id"]
    form_excluded_columns = ["name"]
    column_filters = ("enabled",)
