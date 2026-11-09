import enum
from typing import Dict, List, Optional, Tuple
from uuid import uuid4

from flask_sqlalchemy import BaseQuery
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from server import db
from server.models import QuestionChoice, Subject
from server.models.base_model import BaseModelMixin
from server.models.knowledge_item import KnowledgeItem
from server.models.teacher import Teacher
from server.models.topic import Topic
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


class AdminQuestionChoiceValidator(BaseModel):
    model_config = ConfigDict(extra="allow")

    value: str
    feedback: str
    weight: int = 0
    is_correct_choice: bool = False


class AdminFormValidator(BaseModel):
    model_config = ConfigDict(extra="allow")

    question: str
    question_type: QuestionTypeEnum
    choices: List[AdminQuestionChoiceValidator]
    exam_board: str
    user_created: bool
    subject: str
    topic: str
    knowledge_item: str
    tag: Optional[str] = None
    teacher_id: Optional[int] = None

    @field_validator("question_type", mode="before")
    @classmethod
    def _coerce_question_type(cls, value):
        if isinstance(value, str):
            try:
                return QuestionTypeEnum[value]
            except KeyError:
                raise ValueError(f"Invalid question type: {value}") from None
        return value

    @field_validator("teacher_id")
    @classmethod
    def _validate_teacher_id(cls, value):
        if value is not None and Teacher.query.filter_by(id=value).count() == 0:
            raise ValueError("Teacher not found.")
        return value


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
    tag = db.Column(db.String(128), nullable=True)
    correct_choice_id = db.Column(db.Integer, nullable=False)
    choices = db.relationship("QuestionChoice", backref="question")

    knowledge_item_id = db.Column(db.Integer, db.ForeignKey("knowledge_items.id"), nullable=False)
    knowledge_item = db.relationship("KnowledgeItem")

    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=False)
    topic = db.relationship("Topic")

    user_created = db.Column(db.Boolean, nullable=False, default=False)
    search_vector = db.Column(TSVectorType("question"))

    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship('Subject')

    image_url = db.Column(db.Text, nullable=True)

    def __init__(
        self,
        question: str,
        question_type: 'enum.Enum',
        knowledge_item: KnowledgeItem,
        topic: Topic,
        tag: Optional[str] = None,
        correct_choice_id: Optional[int] = None,
        user_created: bool = False,
        subject_id: Optional[str] = None,
        teacher_id: Optional[int] = None,
        exam_board: Optional[str] = None,
        knowledge_item_id: Optional[int] = None,
        topic_id: Optional[int] = None,
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
        self.knowledge_item_id = knowledge_item_id
        self.topic_id = topic_id
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
        try:
            AdminFormValidator.model_validate(data)
        except ValidationError as exc:
            # Replicate marshmallow's ``partial=True``: missing fields are
            # ignored, but any field that is present must still validate.
            real_errors = [e for e in exc.errors() if e.get("type") != "missing"]
            if real_errors:
                raise ValidationError.from_exception_data(
                    "Error creating question. Make sure that you have filled in "
                    "all the required fields.",
                    real_errors,
                ) from None

        subject_ = Subject.query.filter(Subject.name == data.pop('subject')).first()
        topic_str = data.pop('topic')
        ki_str = data.pop('knowledge_item')
        topic = Topic.query.filter(Topic.value == topic_str).first()
        if topic is None:
            topic = Topic(subject_id=subject_.id, value=topic_str)
            topic.save()
        ki = KnowledgeItem.query.filter(KnowledgeItem.value == ki_str).first()
        if ki is None:
            ki = KnowledgeItem(value=ki_str,
                               topic_id=topic.id, subject_id=subject_.id)
            ki.save()
        choices = data.pop("choices")
        instance = cls(
            data.pop("question"),
            data.pop("question_type"),
            ki,
            topic,
            subject_id=subject_.id,
            **data
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
                choice.get("weight", 0),
                user_created=choice.get("user_created", False),
                teacher_id=choice.get("teacher_id", None)
            )
            if interim.value == '':
                continue
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
