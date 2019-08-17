from server import db
from datetime import datetime

class SchoolClass(db.Model):
    __tablename__ = 'school_class'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    subject = db.Column(db.String(256), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)

    quizzes = db.relationship('ClassQuiz', backref='school_class', lazy=True)
    
    def __repr__(self):
        return '<SchoolClass %r>' % self.name