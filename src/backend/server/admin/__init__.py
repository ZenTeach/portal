from flask_admin.contrib.sqla import ModelView

from .views import QuestionView, SchoolClassView, StudentView, TeacherView, ClassQuizView

__all__ = ['QuestionView', 'SchoolClassView', 'StudentView', 'TeacherView', 'ClassQuizView']
