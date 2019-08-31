from server import db
from server.models.base_model import BaseModelMixin
from datetime import datetime

class SchoolClass(BaseModelMixin, db.Model):
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

    def to_json(self):
        return {
            'name': self.name,
            'subject': self.subject,
            'start_date': str(self.start_date)
        }