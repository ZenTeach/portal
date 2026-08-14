"""
    isort:skip_file
"""

from .question_choice import QuestionChoice
from .subjects import Subject
from .questions import Questions, QuestionTypeEnum
from .quiz_session import QuizSession, QuizSessionStatus
from .quiz_grade import QuizGrade
from .class_quiz import ClassQuiz, ClassQuizStatus
from .student_school_class import StudentAttendedClass
from .school_class import SchoolClass
from .student import Student
from .teacher import Teacher
from .topic import Topic
from .knowledge_item import KnowledgeItem
from .admin import Admin
from .migrations.seeds import run_seed
from .setting import Setting
from .invitations import Invitations
from .activity_log import ActivityLog

__all__ = [
    "ActivityLog",
    "ClassQuiz",
    "ClassQuizStatus",
    "ClassQuizSchema",
    "Teacher",
    "TeacherSchema",
    "QuizSession",
    "QuizSessionStatus",
    "QuizGrade",
    "StudentAttendedClass",
    "Student",
    "Subject",
    "SubjectSchema",
    "StudentSchema",
    "SchoolClass",
    "SchoolClassSchema",
    "Setting",
    "SettingSchema",
    "Admin",
    "QuizSession",
    "Questions",
    "QuestionTypeEnum",
    "QuestionChoice",
    "Invitations",
    "QuestionsSchema",
    "Topic",
    "KnowledgeItem",
    "run_seed",
]


# Flask-free Pydantic v2 schemas. Exposed lazily (rather than imported here)
# so ``from server.models import XSchema`` keeps working across the app while
# avoiding a circular import: ``server.schemas`` imports the ORM model classes
# from this package, which would otherwise re-import ``server.schemas``.
_SCHEMA_NAMES = frozenset(
    {
        "ActivityLogSchema",
        "AdminSchema",
        "ClassQuizSchema",
        "KnowledgeItemSchema",
        "QuestionChoicesSchema",
        "QuestionsSchema",
        "QuizGradeSchema",
        "SchoolClassSchema",
        "SettingSchema",
        "StudentSchema",
        "SubjectSchema",
        "TeacherSchema",
        "TopicSchema",
    }
)


def __getattr__(name: str):
    if name in _SCHEMA_NAMES:
        from server import schemas as _schemas

        return getattr(_schemas, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
