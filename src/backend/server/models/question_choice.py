from server.models.base_model import BaseModelMixin
from server import db

class QuestionChoice(db.Model, BaseModelMixin):
    __tablename__ = 'question_choice'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    value = db.Column(db.String(256), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)

    def __init__(self, value, weight=0):
        self.value = value
        self.weight = weight
