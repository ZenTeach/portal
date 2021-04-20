from server import db
from server.models.base_model import BaseModelMixin


class Subject(db.Model, BaseModelMixin):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    remark = db.Column(db.String(256))

    # One to one relationship with question
    # question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    # question = db.relationship("Questions", back_populates="subjects")

    # One to one relationship with school class
    # question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    # question = db.relationship("Questions", back_populates="subjects")
