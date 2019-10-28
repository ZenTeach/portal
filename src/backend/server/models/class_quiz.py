from server import db
from .base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import JSON
import enum
from datetime import datetime

__all__ = ['ClassQuizStatus', 'ClassQuiz', 'ClassQuizSchema']


class ClassQuizStatus (enum.Enum):
    created = 1
    administered = 2
    cancelled = 3


class ClassQuiz(BaseModelMixin, db.Model):
    __tablename__ = 'class_quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    questions = db.Column(JSON)

    def __repr__(self):
        return '<ClassQuiz %r>' % self.name
