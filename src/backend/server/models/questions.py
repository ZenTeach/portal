from server import db
from sqlalchemy.dialects.postgresql import JSON
from server.models.base_model import BaseModelMixin
from sqlalchemy_utils.types import TSVectorType
from sqlalchemy_searchable import SearchQueryMixin
from flask_sqlalchemy import BaseQuery
import enum

class QuestionsQuery(BaseQuery, SearchQueryMixin):
    pass

class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3


class Questions(BaseModelMixin, db.Model):
    __tablename__ = 'questions'
    query_class = QuestionsQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(
        db.Enum(QuestionTypeEnum), nullable=False, default=QuestionTypeEnum.multiple_choice)
    subject = db.Column(db.String(256), nullable=False)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    choices = db.Column(JSON)
    knowledge_item = db.Column(db.String(256), nullable=False)
    search_vector = db.Column(TSVectorType('question'))
