from server import db
from server.models.base_model import BaseModelMixin


class Subject(db.Model, BaseModelMixin):
    __tablename__ = "subjects"

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(256), nullable=False)
    enabled: bool = db.Column(db.Boolean, nullable=False, default=False)
    remark: str = db.Column(db.String(256))

    def __repr__(self) -> str:
        return f'{self.name}'
