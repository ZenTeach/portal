from server import db
from server.models.base_model import BaseModelMixin


class Topic(BaseModelMixin, db.Model):
    __tablename__ = 'topics'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String(256), nullable=False)
