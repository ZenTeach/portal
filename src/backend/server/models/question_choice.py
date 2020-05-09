from server.models.base_model import BaseModelMixin
from server.models import ChoiceFeedback as FeedbackModel
from server import db
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

class QuestionChoice(db.Model, BaseModelMixin):
    __tablename__ = 'question_choice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    value = db.Column(db.String(256), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    feedback = db.relationship('ChoiceFeedback', uselist=False, back_populates='choice')
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=False)

    def __init__(self, value, feedback, weight=0, uuid=uuid4()):
        self.value = value
        self.weight = weight
        self.uuid = uuid
        self.feedback = FeedbackModel(feedback)

    def __repr__(self):
        return 'Choice: {}'.format(self.value)
