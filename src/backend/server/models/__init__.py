"""
    isort:skip_file
"""

from marshmallow_enum import EnumField
from server import ma

from .quiz_session import QuizSession, QuizSessionStatus
from .quiz_grade import QuizGrade
from .class_quiz import ClassQuiz, ClassQuizStatus
from .student_school_class import StudentAttendedClass
from .school_class import SchoolClass
from .student import Student
from .teacher import Teacher
from .admin import Admin
from .feedback import ChoiceFeedback
from .question_choice import QuestionChoice
from .questions import Questions, QuestionTypeEnum
from .topic import Topic
from .migrations.seeds import run_seed

__all__ = [
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
    "StudentSchema",
    "SchoolClass",
    "SchoolClassSchema",
    "ClassQuizScore",
    "Admin",
    "QuizSession",
    "Questions",
    "QuestionTypeEnum",
    "QuestionChoice",
    "QuestionsSchema",
    "ChoiceFeedback",
    "Topic",
    "run_seed",
]


class QuizGradeSchema(ma.ModelSchema):
    class Meta:
        model = QuizGrade
        fields = ("score", "grade_breakdown")


class QuestionChoicesSchema(ma.ModelSchema):
    class Meta:
        model = QuestionChoice
        fields = ("value", "uuid")


class QuestionsSchema(ma.ModelSchema):
    class Meta:
        model = Questions
        fields = (
            "id",
            "question",
            "question_type",
            "subject",
            "topic",
            "knowledge_item",
            "tag",
            "choices",
        )

    question_type = EnumField(QuestionTypeEnum, by_value=True)
    choices = ma.Nested(QuestionChoicesSchema, many=True)


class ClassQuizSchema(ma.ModelSchema):
    class Meta:
        model = ClassQuiz

    status = EnumField(ClassQuizStatus)


class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student
        fields = (
            "id",
            "firstname",
            "lastname",
            "email",
            "date_of_birth",
            "role",
            "classes",
            "quiz_grades",
        )

    classes = ma.List(
        ma.HyperlinkRelated("school_class.schoolclass",
                            url_key="school_class_id")
    )


class AdminSchema(ma.ModelSchema):
    class Meta:
        model = Admin
        fields = (
            "id",
            "firstname",
            "lastname",
            "email",
            "date_of_birth",
            "role",
            "classes",
        )


class SchoolClassSchema(ma.ModelSchema):
    class Meta:
        model = SchoolClass
        fields = ("id", "name", "subject", "start_date", "students", "quizzes")

    quizzes = ma.Nested(ClassQuizSchema, many=True)
    students = ma.Nested(StudentSchema, many=True)


class TeacherSchema(ma.ModelSchema):
    class Meta:
        fields = (
            "id",
            "firstname",
            "lastname",
            "email",
            "date_of_birth",
            "role",
            "classes",
        )
        model = Teacher

    classes = ma.Nested(SchoolClassSchema, many=True)
