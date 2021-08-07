from server import db
from server.models.base_model import BaseModelMixin


class KnowledgeItem(db.Model, BaseModelMixin):
    __tablename__ = 'knowledge_items'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    questions = db.relationship("Questions", lazy=True)
