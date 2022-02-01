from typing import Optional

from server import db
from server.models import Teacher
from server.models.base_model import BaseModelMixin


# Teacher activity log
class ActivityLog(BaseModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Current user
    actor_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    actor = db.relationship('Teacher', backref=db.backref('activity_logs', lazy='dynamic'))

    # Action name
    action = db.Column(db.String(128), nullable=False)

    # Object
    item_type = db.Column(db.String(128), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)

    # Note
    note = db.Column(db.Text, nullable=True)

    # TODO: Remove this after moving to TimeStampMixin
    created = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

    @classmethod
    def log(cls,
            actor: Teacher,
            action: str,
            item_type: str,
            item_id: int,
            note: Optional[str] = None):
        log = cls(
            actor=actor,
            action=action,
            item_type=item_type,
            item_id=item_id,
            note=note)
        log.save()
