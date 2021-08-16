from flask import flash, redirect, url_for
from server.models import Teacher

from .base_view import BaseView, date_format, report_5xx_error


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
