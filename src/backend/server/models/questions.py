from server import db
from sqlalchemy.dialects.postgresql import JSON
from server.models.base_model import BaseModelMixin
import enum


class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3


class Questions(BaseModelMixin, db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.String(256), nullable=False)
    question_type = db.Column(
        db.Enum(QuestionTypeEnum), nullable=False, default=QuestionTypeEnum.multiple_choice)
    subject = db.Column(db.String(256), nullable=False)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    choices = db.Column(JSON)
    question_weights = db.Column(db.Integer, nullable=False)
