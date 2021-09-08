import enum
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from flask_sqlalchemy import BaseQuery
from marshmallow import INCLUDE, Schema, ValidationError, fields
from marshmallow_enum import EnumField
from server import db
from server.models import QuestionChoice, Subject
from server.models.base_model import BaseModelMixin
from server.models.teacher import Teacher
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

from .base_model import unique_uuid4


class QuestionsQuery(BaseQuery, SearchQueryMixin):
    pass


class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3


class AdminQuestionChoiceValidator(Schema):
    class Meta:
        unknown = INCLUDE

    value = fields.Str(required=True)
    feedback = fields.Str(required=True)
    weight = fields.Int()
    is_correct_choice = fields.Bool()

# Server side validation


def validate_teacher_id(id) -> bool:
    return Teacher.query.filter_by(id=id).count() > 0


class AdminFormValidator(Schema):
    class Meta:
        unknown = INCLUDE

    question = fields.Str(required=True)
    question_type = EnumField(QuestionTypeEnum, required=True)
    choices = fields.Nested(AdminQuestionChoiceValidator, required=True, many=True)
    exam_board = fields.Str(required=True)
    user_created = fields.Boolean(required=True)
    subject = fields.Str(required=True)
    topic = fields.Str(required=True)
    tag = fields.Str(required=True)
    knowledge_item = fields.Str(required=True)
    user_created = fields.Boolean(required=True)
    teacher_id = fields.Int(required=True,
                            validate=validate_teacher_id,
                            error_messages={
                                'invalid': 'Teacher not found.'
                            })


class Questions(BaseModelMixin, db.Model):
    __tablename__ = "questions"
    query_class = QuestionsQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(
        db.Enum(QuestionTypeEnum),
        nullable=False,
        default=QuestionTypeEnum.multiple_choice,
    )

    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), nullable=True)

    exam_board = db.Column(db.Text, nullable=True)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    correct_choice_id = db.Column(db.Integer, nullable=False)
    choices = db.relationship("QuestionChoice", backref="question")
    knowledge_item = db.Column(db.String(256), nullable=False)

    _knowledge_item_id = db.Column(db.Integer, db.ForeignKey("knowledge_items.id"), nullable=True)
    _knowledge_item = db.relationship("KnowledgeItem")

    _topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True)
    _topic = db.relationship("Topic")

    user_created = db.Column(db.Boolean, nullable=False, default=False)
    search_vector = db.Column(TSVectorType("question"))

    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship('Subject')

    image_url = db.Column(db.Text, nullable=True)

    def __init__(
        self,
        question: str,
        question_type: 'enum.Enum',
        topic: str,
        tag: str,
        knowledge_item: str,
        correct_choice_id: Optional[int] = None,
        user_created: bool = False,
        subject_id: Optional[str] = None,
        teacher_id: Optional[int] = None,
        exam_board: Optional[str] = None,
        _knowledge_item_id: Optional[int] = None,
        _topic_id: Optional[int] = None,
        uuid: Optional[UUID] = None,
        choices: Optional[List[QuestionChoice]] = [],
        image_url: str = "",
        **kwargs
    ):

        self.question = question
        self.question_type = question_type
        self.subject_id = subject_id
        self.topic = topic
        self.tag = tag
        self.knowledge_item = knowledge_item
        self.user_created = user_created
        self.exam_board = exam_board
        self._knowledge_item_id = _knowledge_item_id
        self._topic_id = _topic_id
        if uuid is None:
            self.uuid = unique_uuid4()

        # self.uuid = uuid
        self.teacher_id = teacher_id
        correct_choice = None
        if isinstance(choices, list) and len(choices) > 0:
            self.choices, correct_choice = self.create_choices_from_list(choices)

        self.correct_choice_id = correct_choice_id or correct_choice
        self.image_url = image_url

    @classmethod
    def create_from_admin_form(cls, data: Dict):
        # We ignore all missing fields here. The most likely missing field
        # is teacher_id as this method is only called from the admin portal.
        # https://stackoverflow.com/questions/55795258/validating-optional-field-in-marshmallow

        validation_errors = AdminFormValidator().validate(data=data, partial=True)
        if validation_errors is not None and len(validation_errors) != 0:
            raise ValidationError(
                "Error creating question. Make sure that you have filled in all the required fields.", validation_errors)  # noqa

        subject_ = Subject.query.filter(Subject.name == data['subject']).first()
        choices = data.pop("choices")
        instance = cls(
            data["question"],
            data["question_type"],
            data["topic"],
            data["tag"],
            data["knowledge_item"],
            subject_id=subject_.id
        )
        instance.choices, instance.correct_choice_id = instance.create_choices_from_list(choices)
        instance.save()
        return instance

    def create_choices_from_list(self,
                                 choice_list: List[dict]) -> Tuple[List[QuestionChoice], int]:
        correct_choice_id = None
        choices = []
        for choice in choice_list:
            interim = QuestionChoice(
                choice.get("value", ""),
                choice.get("feedback", ""),
                choice.get("weight", 0)
            )
            interim.save()
            if choice.get("is_correct_choice", False) and correct_choice_id is None:
                correct_choice_id = interim.id
            choices.append(interim)
        return choices, correct_choice_id

    def correct_choice(self) -> Optional[QuestionChoice]:
        if self.correct_choice_id is None:
            return None
        choice = QuestionChoice.query.filter_by(id=self.correct_choice_id).first()

        if choice is None:
            return None

        return choice

    def __repr__(self) -> str:
        return f"Question {self.question}"

    @classmethod
    def empty_instance(cls):
        return cls(
            question='',
            question_type='',
            topic='',
            tag='',
            knowledge_item=''
        )
