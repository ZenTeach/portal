import enum
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from flask import current_app
from server import db
from sqlalchemy import event, text
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
    max_score = db.Column(db.Integer, nullable=True)
    variants = db.Column(db.Integer, nullable=True, default=1)
    name = db.Column(db.String(256), nullable=True)
    status = db.Column(
        db.Enum(ClassQuizStatus), nullable=False, default=ClassQuizStatus.created
    )
    class_id = db.Column(db.Integer, db.ForeignKey(
        "school_class.id"), nullable=False)

    # TODO: Delete these
    held_on = db.Column(db.DateTime, nullable=True)
    gform_id = db.Column(db.String(128), nullable=True)
    script_id = db.Column(db.String(128), nullable=True, default=None)
    private = db.Column(db.Boolean, server_default='true')

    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    questions = db.Column(JSON)
    url = db.Column(db.String(256), nullable=True, default=None)

    student_quiz_sessions = db.relationship(
        "Student", secondary="quiz_session", viewonly=True
    )

    student_quiz_grades = db.relationship(
        "Student", secondary="quiz_grade", viewonly=True, lazy='subquery'
    )

    def __init__(
        self,
        subject: str,
        class_id: int,
        max_score: Optional[int] = None,
        variants: Optional[int] = 0,
        questions: Optional[JSON] = None,
        name: Optional[str] = None,
        status: 'ClassQuizStatus' = ClassQuizStatus.created,
        url: Optional[str] = None,
        private: Optional[bool] = True,
        uuid: Optional[UUID] = None,
        **kwargs
    ):
        self.subject = subject
        self.max_score = max_score
        self.variants = variants
        self.status = status
        self.class_id = class_id
        self.questions = questions
        if max_score is None:
            self.max_score = self.set_maxscore()
        else:
            self.max_score = max_score

        if uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid

        if name is None:
            self.name = self.set_default_quizname()
        else:
            self.name = name
        self.private = private

    def __repr__(self):
        return "<ClassQuiz %r>" % self.id

    def update_status(self, new_status):
        self.status = new_status
        self.save()

    def add_student_session(self, student):
        from .quiz_session import QuizSession

        self.student_quiz_sessions.append(
            QuizSession(student=student, class_quiz=self, uuid=unique_uuid4()))

    def set_maxscore(self) -> int:
        if self.questions is not None and len(self.questions) != 0:
            return len(self.questions)
        else:
            return 0

    @property
    def public(self) -> List['ClassQuiz']:
        return self.query.filter_by(private=False).all()

    def set_default_quizname(self) -> str:
        try:
            current_class_count = ClassQuiz.query.filter_by(class_id=self.class_id).count()
            return f"Quiz #{current_class_count + 1}"
        except Exception:
            return 'Default Quiz Name'


@event.listens_for(ClassQuiz, 'after_insert')
def receive_after_insert(mapper, connection, target):
    quiz_url = "{}/quiz_view/{}".format(current_app.config.get('CLIENT_URL'), target.uuid)

    update_stmt = text("UPDATE class_quiz SET url=:url WHERE id=:id")
    update_stmt = update_stmt.bindparams(id=target.id, url=quiz_url)

    connection.execute(update_stmt)
