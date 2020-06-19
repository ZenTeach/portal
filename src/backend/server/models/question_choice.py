from uuid import uuid4

from server import db
from server.models import ChoiceFeedback as FeedbackModel
from server.models.base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID


class QuestionChoice(db.Model, BaseModelMixin):
    __tablename__ = "question_choice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    # referenced_question =  db.relationship('Questions', back_populates="correct_choice")
    value = db.Column(db.String(256), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    feedback = db.relationship(
        "ChoiceFeedback", uselist=False, back_populates="choice")
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())

    def __init__(self, value, feedback, weight=0, uuid=uuid4()):
        self.value = value
        self.weight = weight
        self.uuid = uuid
        if type(feedback) == FeedbackModel:
            self.feedback = feedback
        else:  # string input
            self.feedback = FeedbackModel(feedback)

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
