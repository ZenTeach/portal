from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy.ext.hybrid import hybrid_property


class KnowledgeItem(db.Model, BaseModelMixin):
    __tablename__ = 'knowledge_items'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    questions = db.relationship("Questions", lazy='dynamic')

    def __repr__(self):
        return f"{self.value}"

    @hybrid_property
    def linked_question_count(self):
        return self.questions.count()
