from typing import Optional
from uuid import uuid4

from server import db
from sqlalchemy.dialects.postgresql import JSON, UUID

from .base_model import BaseModelMixin, unique_uuid4


# A many-to-many relationship between a Student and ClassQuiz model
class QuizGrade(BaseModelMixin, db.Model):
    __tablename__ = "quiz_grade"
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())

    student_id = db.Column(db.Integer, db.ForeignKey(
        "student.id"), primary_key=True)

    class_quiz_id = db.Column(
        db.Integer, db.ForeignKey("class_quiz.id"), primary_key=True
    )

    student = db.relationship("Student", backref=db.backref("quiz_grade"))

    class_quiz = db.relationship(
        "ClassQuiz",
        backref=db.backref("student_quiz_grade", cascade="all, delete-orphan")
    )

    score = db.Column(db.Integer, nullable=True)
    graded = db.Column(db.Boolean, nullable=False, default=False)
    grade_breakdown = db.Column(JSON)
    result_sent = db.Column(db.Boolean, nullable=True, default=False)
    responses = db.Column(JSON)

    def __init__(self,
                 student_id: int,
                 class_quiz_id: int,
                 score: Optional[int] = 0,
                 graded: Optional[bool] = False,
                 grade_breakdown: Optional[dict] = {},
                 responses: Optional[dict] = {},
                 result_sent: Optional[bool] = False,
                 uuid: Optional[UUID] = None,
                 ):

        self.student_id = student_id
        self.class_quiz_id = class_quiz_id
        self.score = score
        self.graded = graded
        self.grade_breakdown = grade_breakdown
        self.responses = responses
        self.result_sent = result_sent

        if uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid

    def __repr__(self) -> str:
        return f"<QuizGrade {self.class_quiz.subject} {self.student.full_name}>"

    def update_score(self, new_score):
        self.score = new_score
        self.save()

    def update_grade_breakdown(self, grade_breakdown):
        self.grade_breakdown = grade_breakdown
        self.save()

    def is_graded(self):
        self.graded = True
        self.save()

    def prepare_regrade_(self):
        if not self.graded:
            raise Exception("Quiz has not been graded yet!")

        self.grade_breakdown = {}
        self.save()
