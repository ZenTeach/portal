from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy.ext.hybrid import hybrid_property


class Topic(db.Model, BaseModelMixin):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(255), nullable=False)
    questions = db.relationship("Questions", lazy='dynamic')
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship("Subject", lazy='joined', uselist=False)

    def __repr__(self):
        return f"{self.value}"

    @hybrid_property
    def linked_question_count(self):
        return self.questions.count()
