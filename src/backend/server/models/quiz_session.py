import enum
from datetime import datetime
from uuid import uuid4

from server import db
from sqlalchemy.dialects.postgresql import UUID

from .base_model import BaseModelMixin


class QuizSessionStatus(enum.Enum):
    created = 1
    ended = 2


class QuizSession(BaseModelMixin, db.Model):
    __tablename__ = "quiz_session"

    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())

    student_id = db.Column(db.Integer, db.ForeignKey(
        "student.id"), primary_key=True)
    class_quiz_id = db.Column(
        db.Integer, db.ForeignKey("class_quiz.id"), primary_key=True
    )

    student = db.relationship("Student", backref=db.backref("quiz_session"))
    class_quiz = db.relationship(
        "ClassQuiz", backref=db.backref("quiz_session"))

    start_time = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    end_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    timer = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(
        db.Enum(QuizSessionStatus), nullable=False, default=QuizSessionStatus.created
    )

    def __repr__(self):
        return "<QuizSession {}>".format(
            self.class_quiz.subject + " " + self.student.full_name()
        )

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def has_session_ended(self):
        return self.status == QuizSessionStatus.ended
