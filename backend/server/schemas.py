"""Pydantic v2 schemas for the FastAPI layer.

These reproduce the wire format of the legacy marshmallow schemas declared in
:mod:`server.models` exactly, so the ported FastAPI routers can (de)serialize
ORM objects without Flask or marshmallow.

Every schema uses ``from_attributes=True`` so ORM instances can be validated
directly with :meth:`pydantic.BaseModel.model_validate`. The
:class:`ORMSchema` base provides ``dump_one``/``dump_many`` helpers that emit
JSON-safe dicts (``model_dump(mode="json")``).

Notes on intentional deviations from the marshmallow schemas:

* ``StudentSchema.classes`` used ``ma.HyperlinkRelated`` to build Flask
  ``url_for`` hyperlinks. That is a hard Flask dependency, so the Pydantic
  port emits a list of school-class IDs instead.
* ``QuestionChoicesSchema.is_correct_choice``, ``ClassQuizSchema.submissions``
  and ``SchoolClassSchema.key_stage`` are computed fields reproduced from the
  model layer.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_serializer

from server.models import (
    ActivityLog,
    Admin,
    ClassQuiz,
    ClassQuizStatus,
    KnowledgeItem,
    QuestionChoice,
    Questions,
    QuestionTypeEnum,
    QuizGrade,
    QuizSession,
    QuizSessionStatus,
    SchoolClass,
    Setting,
    Student,
    StudentAttendedClass,
    Subject,
    Teacher,
    Topic,
)
from server.models.school_class import KEYSTAGE_MAP


class ORMSchema(BaseModel):
    """Base schema that can be built directly from an ORM object."""

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def dump_one(cls, obj: Any) -> dict:
        """Serialize a single ORM object to a JSON-safe dict."""
        return cls.model_validate(obj).model_dump(mode="json")

    @classmethod
    def dump_many(cls, objs: List[Any]) -> List[dict]:
        """Serialize a list of ORM objects to JSON-safe dicts."""
        return [cls.dump_one(obj) for obj in objs]


class SubjectSchema(ORMSchema):
    id: int
    name: str
    enabled: bool
    remark: Optional[str] = None


class SubjectNameSchema(ORMSchema):
    name: str


class QuestionChoicesSchema(ORMSchema):
    value: str
    uuid: UUID
    feedback: Optional[str] = None
    weight: int
    # Source columns for the computed field below (not part of the payload).
    id: Optional[int] = Field(default=None, exclude=True)
    question_id: Optional[int] = Field(default=None, exclude=True)

    @computed_field
    @property
    def is_correct_choice(self) -> bool:
        if self.question_id is None:
            return False
        question = Questions.query.filter_by(id=self.question_id).first()
        return bool(question and question.correct_choice_id == self.id)


class TopicValueSchema(ORMSchema):
    value: str


class TopicSchema(ORMSchema):
    value: str
    subject: Optional[SubjectSchema] = None
    teacher_id: Optional[int] = None


class KnowledgeItemValueSchema(ORMSchema):
    value: str


class KnowledgeItemSchema(ORMSchema):
    value: str
    subject: Optional[SubjectSchema] = None
    teacher_id: Optional[int] = None
    topic: Optional[TopicValueSchema] = None


class QuestionsSchema(ORMSchema):
    id: int
    question: str
    question_type: QuestionTypeEnum
    subject: Optional[SubjectNameSchema] = None
    topic: Optional[TopicValueSchema] = None
    knowledge_item: Optional[KnowledgeItemValueSchema] = None
    tag: Optional[str] = None
    user_created: bool
    exam_board: Optional[str] = None
    choices: List[QuestionChoicesSchema] = Field(default_factory=list)

    @field_serializer("question_type")
    def _serialize_question_type(self, value: Any, _info: Any) -> Any:
        # marshmallow_enum EnumField(by_value=True) emitted the enum's value.
        return value.value if isinstance(value, QuestionTypeEnum) else value


class ClassQuizSchema(ORMSchema):
    id: int
    uuid: Optional[UUID] = None
    subject: str
    max_score: Optional[int] = None
    variants: Optional[int] = None
    name: Optional[str] = None
    status: ClassQuizStatus
    private: Optional[bool] = None
    created: Optional[datetime] = None
    url: Optional[str] = None
    questions: Optional[Any] = None
    # Source column for the submissions computed field (not in the payload).
    class_id: Optional[int] = Field(default=None, exclude=True)

    @field_serializer("status")
    def _serialize_status(self, value: Any, _info: Any) -> Any:
        # marshmallow_enum EnumField (default) emitted the enum's name.
        return value.name if isinstance(value, ClassQuizStatus) else value

    @computed_field
    @property
    def submissions(self) -> str:
        submitted = QuizSession.query.filter_by(
            class_quiz_id=self.id, status=QuizSessionStatus.ended
        ).count()
        student_count = StudentAttendedClass.query.filter_by(
            school_class_id=self.class_id
        ).count()
        return f"{submitted}/{student_count}"


class StudentEmailSchema(ORMSchema):
    email: str


class StudentNoClassesSchema(ORMSchema):
    id: int
    firstname: str
    lastname: str
    email: str
    # Student has no ``date_of_birth`` column, so this is always None.
    date_of_birth: Optional[datetime] = None
    confirmed: Optional[bool] = None


class StudentSchema(ORMSchema):
    id: int
    firstname: str
    lastname: str
    email: str
    date_of_birth: Optional[datetime] = None
    confirmed: Optional[bool] = None
    # Raw relationship, consumed by the computed ``classes`` field below.
    classes_objs: List[Any] = Field(
        default_factory=list, exclude=True, validation_alias="classes"
    )

    @computed_field
    @property
    def classes(self) -> List[int]:
        return [school_class.id for school_class in self.classes_objs]


class SchoolClassSchema(ORMSchema):
    id: int
    name: str
    subject: Optional[SubjectNameSchema] = None
    exam_board: Optional[str] = None
    start_date: Optional[datetime] = None
    year_group: Optional[str] = None
    students: List[StudentNoClassesSchema] = Field(default_factory=list)
    quizzes: List[ClassQuizSchema] = Field(default_factory=list)
    # Source column for the computed ``key_stage`` field below.
    key_stage_code: Optional[str] = Field(
        default=None, exclude=True, validation_alias="key_stage"
    )

    @computed_field
    @property
    def key_stage(self) -> str:
        code = self.key_stage_code
        if code == "" or code is None:
            return ""
        entry = KEYSTAGE_MAP.get(code)
        return entry["name"] if entry else ""


class TeacherSchema(ORMSchema):
    id: int
    firstname: str
    lastname: str
    email: str
    date_of_birth: Optional[datetime] = None
    classes: List[SchoolClassSchema] = Field(default_factory=list)
    confirmed: Optional[bool] = None


class AdminSchema(ORMSchema):
    id: int
    firstname: str
    lastname: str
    email: str
    date_of_birth: Optional[datetime] = None
    role: str
    classes: List[int] = Field(default_factory=list)


class QuizGradeSchema(ORMSchema):
    uuid: UUID
    score: Optional[int] = None
    grade_breakdown: Optional[Any] = None
    student: StudentEmailSchema


class ActivityLogSchema(ORMSchema):
    item_id: int
    item_type: str
    action: str
    note: Optional[str] = None
    created: Optional[datetime] = None


class SettingSchema(ORMSchema):
    appsettings: Any = Field(validation_alias="configuration")


__all__ = [
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
]
