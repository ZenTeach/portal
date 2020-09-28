import enum
from uuid import uuid4

from flask_sqlalchemy import BaseQuery
from marshmallow import INCLUDE, Schema, ValidationError, fields
from server import db
from server.models import QuestionChoice
from server.models.base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType


class QuestionsQuery(BaseQuery, SearchQueryMixin):
    pass


class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3


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

    def __init__(
        self,
        question,
        question_type,
        subject,
        topic,
        tag,
        knowledge_item,
        correct_choice_id,
        uuid=uuid4(),
        choices=[],
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
        self.uuid = uuid
        self.correct_choice_id = correct_choice_id
        self.choices = choices

    @classmethod
    def create_from_admin_form(cls, data):
        # create choices
        created_choice = []
        correct_choice_id = None
        for choice in data["choices"]:
            interim = QuestionChoice(
                choice["value"], choice["feedback"], choice["weight"], uuid4()
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
            uuid=uuid4(),
            choices=created_choice,
        )
        instance.save()
        # instance.set_correct_choice()

    @classmethod
    def empty_instance(cls):
        return cls()
