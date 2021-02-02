from uuid import uuid4

from server import db
from sqlalchemy.dialects.postgresql import JSON, UUID

from .base_model import BaseModelMixin


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
        "ClassQuiz", backref=db.backref("student_quiz_grade"))

    score = db.Column(db.Integer, nullable=True)
    graded = db.Column(db.Boolean, nullable=False, default=False)
    grade_breakdown = db.Column(JSON)
    responses = db.Column(JSON)

    def __repr__(self):
        return "<QuizGrade {}>".format(
            self.class_quiz.subject + " " + self.student.full_name
        )

    def update_score(self, new_score):
        self.score = new_score
        self.save()

    def update_grade_breakdown(self, grade_breakdown):
        self.grade_breakdown = grade_breakdown
        self.save()

    def is_graded(self):
        self.graded = True
        self.save()
