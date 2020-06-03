from server import db
from server.models.base_model import BaseModelMixin
from datetime import datetime
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event

class SchoolClass(BaseModelMixin, db.Model):
    __tablename__ = 'school_class'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    name = db.Column(db.String(256), nullable=False)
    subject = db.Column(db.String(256), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teacher.id'), nullable=True)

    students = db.relationship(
        'Student', secondary="student_attended_class", viewonly=True)

    quizzes = db.relationship('ClassQuiz', backref='school_class', lazy=True)

    def __repr__(self):
        return '<Classroom: %r>' % self.name

    def add_student(self, student):
        from .student_school_class import StudentAttendedClass
        self.student_attended_classes.append(
            StudentAttendedClass(student=student, school_class=self))
