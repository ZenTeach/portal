from datetime import datetime
from typing import Optional

from server import db
from server.models.base_model import BaseModelMixin, unique_uuid4
from sqlalchemy.dialects.postgresql import UUID


class SchoolClass(BaseModelMixin, db.Model):
    __tablename__ = "school_class"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    name = db.Column(db.String(256), nullable=False)
    subject = db.Column(db.String(256), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)

    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), nullable=True)

    students = db.relationship(
        "Student", secondary="student_attended_class", viewonly=True
    )

    year_group = db.Column(db.String(256), nullable=True)

    quizzes = db.relationship("ClassQuiz",
                              backref="school_class",
                              cascade="all, delete",
                              lazy=True)

    def __init__(self,
                 id: int,
                 name: str,
                 subject: str,
                 start_date: Optional['datetime'] = datetime.now(),
                 teacher_id: Optional[int] = None,
                 year_group: Optional[str] = None,
                 uuid: Optional[UUID] = None
                 ):

        self.id = id
        self.name = name
        self.subject = subject
        self.start_date = start_date
        self.teacher_id = teacher_id
        self.year_group = year_group
        if self.uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid

    def __repr__(self):
        return "<Classroom: %r>" % self.name

    def add_student(self, student):
        from .student_school_class import StudentAttendedClass

        StudentAttendedClass(student=student, school_class=self).save()

    def remove_student(self, student_id):
        from .student_school_class import StudentAttendedClass
        assoc_ = StudentAttendedClass.query\
                                     .filter_by(school_class=self,
                                                student_id=student_id)\
                                     .first()
        db.session.delete(assoc_)
        db.session.commit()

    @classmethod
    def remove_classroom(cls, _class: 'SchoolClass'):
        db.engine.execute(
            "DELETE FROM student_attended_class WHERE school_class_id=%s",
            _class.id,
        )

        _class.delete()
