from typing import Optional
from uuid import uuid4

from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID

from .base_model import unique_uuid4


class QuestionChoice(db.Model, BaseModelMixin):
    __tablename__ = "question_choice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    value = db.Column(db.String(256), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    feedback = db.Column(db.Text, nullable=True, default="")
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())

    def __init__(self,
                 value: str,
                 feedback: str,
                 weight: int = 0,
                 uuid: Optional[UUID] = None,
                 question_id: Optional[int] = None):
        self.value = value
        self.weight = weight
        if uuid is None:
            self.uuid = unique_uuid4()
        self.feedback = feedback
        if question_id is not None:
            self.question_id = question_id

    @property
    def is_correct_choice(self):
        if not hasattr(self, "_is_correct_choice"):
            self._is_correct_choice = False

        return self._is_correct_choice

    @is_correct_choice.setter
    def is_correct_choice(self, val):
        self._is_correct_choice = val

    def __repr__(self):
        return "Choice: {}".format(self.value)

    @classmethod
    def empty_instance(cls):
        return cls(value="")
