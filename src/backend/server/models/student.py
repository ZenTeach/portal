from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID

from server import db
from server.models.base_model import BaseModelMixin


class Student(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship('SchoolClass',
                              secondary='student_attended_class', viewonly=True)

    quiz_sessions = db.relationship('ClassQuiz', secondary='quiz_session', viewonly=True)

    # TODO: Fix this relationship, keeps throwing sqlalchemy.exc.NoForeignKeysError
    quiz_grades = db.relationship('ClassQuiz', secondary='quiz_grade', viewonly=True)
    # primaryjoin="Student.id == foreign(QuizGrade.student_id)",
    # foreign_keys='QuizGrade.student_id'

    def __init__(self, firstname, lastname, email, password, date_of_birth, classes, role="Student"):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.password = password
        self.date_of_birth = self.data_of_birth
        self.role = role

    def __repr__(self):
        return '<Student %s>' % (self.firstname + " " + self.lastname)

    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def add_quiz_score(self, quiz, response):
        from .quiz_grade import QuizGrade
        self.quiz_grade.append(
            QuizGrade(student=self, class_quiz=quiz, responses=response)
        )
