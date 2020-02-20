from server import db
from .base_model import BaseModelMixin
from datetime import datetime
import enum
from sqlalchemy.dialects.postgresql import JSON, UUID
from uuid import uuid4

class QuizSessionStatus (enum.Enum):
    created = 1
    ended = 2

class QuizSession(BaseModelMixin, db.Model):
    __tablename__ = 'quiz_session'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True, default=uuid4())

    quiz_uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    student_email = db.Column(db.String(128), nullable=False)

    student_id = db.Column(db.Integer, db.ForeignKey(
        'student.id'), primary_key=True)
    class_quiz_id = db.Column(db.Integer, db.ForeignKey(
        'class_quiz.id'), primary_key=True)

    student = db.relationship(
        "Student", backref=db.backref("quiz_session"))
    class_quiz = db.relationship(
        "ClassQuiz", backref=db.backref("quiz_session"))

    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    end_time = db.Column(db.DateTime, nullable=True,
                           default=datetime.utcnow)
    timer = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    status = db.Column(
        db.Enum(QuizSessionStatus), nullable=False, default=QuizSessionStatus.created)

    def __init__(self, student=None, class_quiz=None):
        self.id = uuid4().hex
        self.student = student
        self.class_quiz = class_quiz

    def __repr__(self):
        return '<QuizSession {}>'.format(self.class_quiz.subject+" "+self.student.full_name())
