from server import db
from server.models.base_model import BaseModelMixin


class ChoiceFeedback(BaseModelMixin, db.Model):
    __tablename__ = "choice_feedback"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    choice_id = db.Column(db.Integer, db.ForeignKey("question_choice.id"))
    choice = db.relationship("QuestionChoice", back_populates="feedback")
    content = db.Column(db.Text, nullable=False, default="")

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return "Feedback: {}".format(self.content)
