from server import db
from server.models.base_model import BaseModelMixin
from server.models.user_account.confirmable import Confirmable
from server.models.user_account.recoverable import Recoverable


class User(BaseModelMixin, db.Model, Confirmable, Recoverable):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(50))

    __mapper_args__ = {
        "polymorphic_identity": "user",
        "polymorphic_on": type,
    }
