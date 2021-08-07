from server import db
from server.models.base_model import BaseModelMixin


class Topic(db.Model, BaseModelMixin):
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(255), nullable=False)
    questions = db.relationship("Questions", lazy=True)
