from .base_view import BaseView


class ClassQuizView(BaseView):
    can_create = False
    column_exclude_list = ["uuid", "questions",
                           "script_id", "gform_id", "created_at", "school_class"]
    form_excluded_columns = [
        "uuid",
        "status",
        "held_on",
        "student_attended_classes",
        "created_at",
        "student",
        "gform_id",
        "script_id",
        "student_quiz_sessions",
        "student_quiz_grades",
        "quiz_session",
        "student_quiz_grade",
    ]
