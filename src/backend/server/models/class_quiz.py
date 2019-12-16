import enum
import json
from datetime import datetime
from uuid import uuid4

from server import db
from sqlalchemy.dialects.postgresql import JSON, UUID

from .base_model import BaseModelMixin

__all__ = ['ClassQuizStatus', 'ClassQuiz', 'ClassQuizSchema']


class ClassQuizStatus (enum.Enum):
    created = 1
    administered = 2
    cancelled = 3


class ClassQuiz(BaseModelMixin, db.Model):
    __tablename__ = 'class_quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    subject = db.Column(db.String(256), nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    variants = db.Column(db.Integer, nullable=True, default=1)
    status = db.Column(
        db.Enum(ClassQuizStatus), nullable=False, default=ClassQuizStatus.created)
    class_id = db.Column(db.Integer, db.ForeignKey(
        'school_class.id'), nullable=False)
    held_on = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    gform_id = db.Column(db.String(128), nullable=True)
    questions = db.Column(JSON)

    def __repr__(self):
        return '<ClassQuiz %r>' % self.id

    def update_gform_id(self, project_id, deployment_id, version_number):
        d = {
            "pid": project_id,
            "dep_id": deployment_id,
            "version": version_number
        }

        self.gform_id = json.dumps(d)

        self.save()
