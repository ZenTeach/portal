import enum
from typing import Dict, List, Optional
from uuid import uuid4

from flask_sqlalchemy import BaseQuery
from marshmallow import INCLUDE, Schema, ValidationError, fields
from marshmallow_enum import EnumField
from server import db
from server.models import QuestionChoice
from server.models.base_model import BaseModelMixin
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


class AdminFormValidator(Schema):
    class Meta:
        unknown = INCLUDE

    question = fields.Str(required=True)
    question_type = EnumField(QuestionTypeEnum, by_value=True, required=True)
    choices = fields.Nested(AdminQuestionChoiceValidator, required=True, many=True)
    subject = fields.Str(required=True)
    topic = fields.Str(required=True)
    tag = fields.Str(required=True)
    knowledge_item = fields.Str(required=True)


class MultipleChoiceSchema(Schema):
    class Meta:
        unknown = INCLUDE

    a = fields.Str(required=True)
    b = fields.Str(required=True)
    c = fields.Str(required=True)
    d = fields.Str(required=True)


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
    subject = db.Column(db.String(256), nullable=False)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    correct_choice_id = db.Column(db.Integer, nullable=False)
    choices = db.relationship("QuestionChoice", backref="question")
    knowledge_item = db.Column(db.String(256), nullable=False)
    search_vector = db.Column(TSVectorType("question"))
    image_url = db.Column(db.Text, nullable=True)

    def __init__(
        self,
        question: str,
        question_type: 'enum.Enum',
        subject: str,
        topic: str,
        tag: str,
        knowledge_item: str,
        correct_choice_id: int,
        uuid: Optional[UUID] = None,
        choices: Optional[List[QuestionChoice]] = [],
        image_url: str = "",
        **kwargs
    ):
        if question_type == QuestionTypeEnum.multiple_choice:
            try:
                MultipleChoiceSchema().validate(data=choices)
            except ValidationError:
                raise

        self.question = question
        self.question_type = question_type
        self.subject = subject
        self.topic = topic
        self.tag = tag
        self.knowledge_item = knowledge_item
        if uuid is None:
            self.uuid = unique_uuid4()

        # self.uuid = uuid
        self.correct_choice_id = correct_choice_id
        self.choices = choices
        self.image_url = image_url

    @classmethod
    def create_from_admin_form(cls, data: Dict):

        validation_errors = AdminFormValidator().validate(data=data)
        if validation_errors is not None and len(validation_errors) != 0:
            raise ValidationError(
                "Error creating question. Make sure that you have filled in all the required fields.", validation_errors)  # noqa
        created_choice = []
        correct_choice_id = None
        for choice in data["choices"]:
            interim = QuestionChoice(
                choice["value"], choice["feedback"], choice["weight"]
            )
            interim.save()
            if choice["is_correct_choice"] and correct_choice_id is None:
                correct_choice_id = interim.id
            created_choice.append(interim)
        instance = cls(
            data["question"],
            data["question_type"],
            data["subject"],
            data["topic"],
            data["tag"],
            data["knowledge_item"],
            correct_choice_id,
            choices=created_choice,
        )
        instance.save()
        return instance

    def correct_choice(self) -> Optional[QuestionChoice]:
        if self.correct_choice_id is None:
            return None
        choice = QuestionChoice.query.filter_by(id=self.correct_choice_id).first()

        if choice is None:
            return None

        return choice
