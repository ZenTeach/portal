from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event

from server import db, bcrypt
from server.models.base_model import BaseModelMixin
import string
import random

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


class Student(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship('SchoolClass',
                              secondary='student_attended_class', viewonly=True)

    quiz_sessions = db.relationship('ClassQuiz', secondary='quiz_session', viewonly=True)

    quiz_grades = db.relationship('ClassQuiz', secondary='quiz_grade', viewonly=True)

    def __init__(self, firstname, lastname, email, classes=[], password=None, role="Student"):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        if password is None:
            self.password = bcrypt.generate_password_hash(randomString())
        else:
            self.password = password
        self.role = role

    def __repr__(self):
        return '<Student %s>' % (self.firstname + " " + self.lastname)

    @property
    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def add_quiz_score(self, quiz, response):
        from .quiz_grade import QuizGrade
        self.quiz_grade.append(
            QuizGrade(student=self, class_quiz=quiz, responses=response)
        )

    @classmethod
    def create_from_list(cls, lst):
        if len(lst) == 0:
            return
        errors = []
        instance = None
        added_students = []
        for it in lst:
            try:
                instance = cls(**it)
                instance.save()
            except Exception as e:
                errors.append(str(e))
            else:
                added_students.append(instance)
        return errors, added_students


@event.listens_for(Student.classes, 'append')
def student_class_append_listener(target, value, initiator):
    value.add_student(target)

@event.listens_for(Student.classes, 'remove')
def student_class_remove_listener(target, value, initiator):
    db.engine.execute("DELETE FROM student_attended_class WHERE school_class_id=%s AND student_id=%s", value.id, target.id)
