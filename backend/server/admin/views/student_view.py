from flask import flash, redirect, url_for
from server.models import Student

from .base_view import BaseView, date_format, logger


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
            flash("Failed to create record: {}".format(str(e)), "error")

    def delete_model(self, model):
        try:
            Student.remove_model(model)
            flash("Successfully deleted student", "success")
        except Exception as e:
            logger.error("Failed to delete record: {}".format(str(e)))
            flash("Failed to delete record: {}".format(str(e)), "error")
