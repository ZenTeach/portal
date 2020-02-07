from server import db
from sqlalchemy.dialects.postgresql import JSON

# A many-to-many relationship between a Student and ClassQuiz model
class_quiz_score = db.Table('class_quiz_scores',
                            db.Column('student_id', db.Integer, db.ForeignKey(
                                'student.id'), primary_key=True),
                            db.Column('quiz_id', db.Integer, db.ForeignKey(
                                'class_quiz.id'), primary_key=True),
                            db.Column('score', db.Integer),
                            db.Column('grade_breakdown', JSON),
                            db.Column('responses', JSON)
                            )
