from server import db
from sqlalchemy.dialects.postgresql import JSON
from server.models.base_model import BaseModelMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import SearchQueryMixin
from random import choices
from flask_sqlalchemy import BaseQuery
import enum
from sqlalchemy.dialects.postgresql import UUID
from marshmallow import Schema, fields, INCLUDE, ValidationError
class QuestionsQuery(BaseQuery, SearchQueryMixin):
    pass

class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3

class MultipleChoiceSchema(Schema):
    class Meta:
        unknown=INCLUDE

    a=fields.Str(required=True)
    b=fields.Str(required=True)
    c=fields.Str(required=True)
    d=fields.Str(required=True)

class Questions(BaseModelMixin, db.Model):
    __tablename__ = 'questions'
    query_class = QuestionsQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(
        db.Enum(QuestionTypeEnum), nullable=False, default=QuestionTypeEnum.multiple_choice)
    subject = db.Column(db.String(256), nullable=False)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    correct_choice = db.Column(db.String(1), nullable=True, default=choices(['a', 'b', 'c', 'd']))
    choices = db.Column(JSON)
    knowledge_item = db.Column(db.String(256), nullable=False)
    search_vector = db.Column(TSVectorType('question'))

    def __init__(self, question, question_type, subject, topic, tag, knowledge_item, uuid, choices={}):
        if question_type == QuestionTypeEnum.multiple_choice:
            try:
                MultipleChoiceSchema().validate(data=choices)
            except ValidationError as err:
                print(err)
                raise

        self.question = question
        self.question_type = question_type
        self.subject = subject
        self.topic = topic
        self.tag = tag
        self.knowledge_item = knowledge_item
        self.uuid = uuid
        self.choices = choices
