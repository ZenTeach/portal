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

    def update_model(self, form, model):
        try:
            selected_ids = {c.id for c in form.data["classes"]}
            current_ids = {c.id for c in model.classes}

            for name, field in form._fields.items():
                if name == "classes":
                    continue
                setattr(model, name, field.data)

            for class_ in model.classes:
                if class_.id not in selected_ids:
                    model.remove_class(class_)

            for class_ in form.data["classes"]:
                if class_.id not in current_ids:
                    model.add_to_class(class_)

            model.save()
            flash("Successfully updated student", "success")
            return model
        except Exception as e:
            logger.error("Failed to update record: {}".format(str(e)))
            flash("Failed to update record: {}".format(str(e)), "error")
