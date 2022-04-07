"""
    isort:skip_file
"""

from marshmallow_enum import EnumField
from marshmallow import Schema, fields
from server import ma

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


class SubjectSchema(ma.Schema):
    class Meta:
        model = Subject
        fields = ("id",
                  "name",
                  "enabled",
                  "remark")


class QuestionChoicesSchema(ma.Schema):
    class Meta:
        model = QuestionChoice
        fields = ("value", "uuid", "feedback", "weight", "is_correct_choice")

    is_correct_choice = ma.Method('_is_correct_choice')

    def _question(self, q_id: int) -> Questions:
        return Questions.query.filter_by(id=q_id).first()

    def _is_correct_choice(self, obj):
        q = self._question(obj.question_id)
        if q.correct_choice_id == obj.id:
            return True

        return False


class TopicSchema(ma.Schema):
    class Meta:
        model = Topic
        fields = ("value", "subject", "teacher_id")

    subject = ma.Nested(SubjectSchema)


class KnowledgeItemSchema(ma.Schema):
    class Meta:
        model = KnowledgeItem
        fields = ("value", "subject", "teacher_id", "topic")

    subject = ma.Nested(SubjectSchema)
    topic = ma.Nested(TopicSchema, only=("value",))


class QuestionsSchema(ma.Schema):
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
            "user_created",
            "exam_board",
            "choices",
        )

    knowledge_item = ma.Nested(KnowledgeItemSchema, only=("value",))
    topic = ma.Nested(TopicSchema, only=("value",))
    question_type = EnumField(QuestionTypeEnum, by_value=True)
    choices = ma.Nested(QuestionChoicesSchema, many=True)
    subject = ma.Nested(SubjectSchema, only=('name',))


class ClassQuizSchema(ma.Schema):
    class Meta:
        model = ClassQuiz

    status = EnumField(ClassQuizStatus)


class StudentSchema(ma.Schema):
    class Meta:
        model = Student
        fields = (
            "id",
            "firstname",
            "lastname",
            "email",
            "date_of_birth",
            "confirmed",
            "classes",
        )

    classes = ma.List(
        ma.HyperlinkRelated("school_class.schoolclass",
                            url_key="school_class_id")
    )


class AdminSchema(ma.Schema):
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


class SchoolClassSchema(ma.Schema):
    class Meta:
        model = SchoolClass
        fields = ("id", "name", "subject", "exam_board", "key_stage",
                  "start_date", "year_group", "students", "quizzes")

    quizzes = ma.Nested(ClassQuizSchema, many=True)
    students = ma.Nested(StudentSchema, many=True)
    subject = ma.Nested(SubjectSchema, only=('name',))
    key_stage = ma.Method('_key_stage_for_api')

    def _key_stage_for_api(self, obj):
        return obj.key_stage_for_front_end()


class TeacherSchema(ma.Schema):
    class Meta:
        fields = (
            "id",
            "firstname",
            "lastname",
            "email",
            "date_of_birth",
            "classes",
            "confirmed"
        )
        model = Teacher

    classes = ma.Nested(SchoolClassSchema, many=True)


class QuizGradeSchema(ma.Schema):
    class Meta:
        model = QuizGrade
        fields = ("uuid",
                  "score",
                  "grade_breakdown",
                  "student")

    student = ma.Nested(StudentSchema)


class ActivityLogSchema(ma.Schema):
    class Meta:
        model = ActivityLog
        fields = ("item_id", "item_type", "action", "note", "created")


class SettingSchema(Schema):
    appsettings = fields.Method('_appsettings')

    def _appsettings(self, obj):
        return obj.configuration
