import enum
import json
from datetime import datetime
from typing import Optional
from uuid import uuid4

from flask import current_app
from server import db
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import JSON, UUID

from .base_model import BaseModelMixin, unique_uuid4

__all__ = ["ClassQuizStatus", "ClassQuiz"]


class ClassQuizStatus(enum.Enum):
    created = 1
    in_progress = 2
    administered = 3
    graded = 4
    cancelled = 5


class ClassQuiz(BaseModelMixin, db.Model):
    __tablename__ = "class_quiz"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=True, default=uuid4())
    subject = db.Column(db.String(256), nullable=False)
    max_score = db.Column(db.Integer, nullable=False)
    variants = db.Column(db.Integer, nullable=True, default=1)
    status = db.Column(
        db.Enum(ClassQuizStatus), nullable=False, default=ClassQuizStatus.created
    )
    class_id = db.Column(db.Integer, db.ForeignKey(
        "school_class.id"), nullable=False)
    held_on = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    script_id = db.Column(db.String(128), nullable=True, default=None)
    gform_id = db.Column(db.String(128), nullable=True)
    questions = db.Column(JSON)
    url = db.Column(db.String(256), nullable=True, default=None)

    student_quiz_sessions = db.relationship(
        "Student", secondary="quiz_session", viewonly=True
    )

    student_quiz_grades = db.relationship(
        "Student", secondary="quiz_grade", viewonly=True
    )

    def __init__(
        self,
        subject: str,
        max_score: int,
        variants: int,
        class_id: int,
        questions: Optional[JSON] = None,
        status: 'ClassQuizStatus' = ClassQuizStatus.created,
        url: Optional[str] = None,
        uuid: Optional[UUID] = None,
        **kwargs
    ):
        self.subject = subject
        self.max_score = max_score
        self.variants = variants
        self.status = status
        self.class_id = class_id
        self.questions = questions
        if self.uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid

    def __repr__(self):
        return "<ClassQuiz %r>" % self.id

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def update_gform_id(self, project_id, deployment_id, version_number):
        d = {"pid": project_id, "dep_id": deployment_id, "version": version_number}

        self.gform_id = json.dumps(d)

        self.save()

    def add_student_session(self, student):
        from .quiz_session import QuizSession

        self.student_quiz_sessions.append(
            QuizSession(student=student, class_quiz=self))


@event.listens_for(ClassQuiz, 'before_insert')
def receive_init(target, args, kwargs):
    quiz_url = "{}/quiz_view/{}".format(current_app.config.get('CLIENT_URL'), kwargs.uuid)
    kwargs.url = quiz_url
