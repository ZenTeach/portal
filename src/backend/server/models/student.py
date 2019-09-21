from server import db
from .quiz_grade import class_quiz_score as quizzes
from server.models.base_model import BaseModelMixin

class Student(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)    
    password = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship('SchoolClass', backref='student', lazy=True)
    quiz_grades = db.relationship('ClassQuiz', secondary=quizzes, lazy='subquery',
        backref=db.backref('students', lazy=True))

    def __repr__(self):
        return '<Student %r>' % self.id
 
    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)       