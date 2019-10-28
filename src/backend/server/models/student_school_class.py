from server import db
import uuid
from .base_model import BaseModelMixin


class StudentAttendedClass(BaseModelMixin, db.Model):
    __tablename__ = 'student_attended_class'

    student_id = db.Column(db.Integer, db.ForeignKey(
        'student.id'), primary_key=True)
    school_class_id = db.Column(db.Integer, db.ForeignKey(
        'school_class.id'), primary_key=True)

    student = db.relationship(
        "Student", backref=db.backref("student_attended_classes"))
    school_class = db.relationship(
        "SchoolClass", backref=db.backref("student_attended_classes"))

    def __init__(self, student=None, school_class=None):
        self.id = uuid.uuid4().hex
        self.student = student
        self.school_class = school_class

    def __repr__(self):
        return '<StudentAttendedClass {}>'.format(self.school_class.name+" "+self.student.full_name())
