from server import db

# A many-to-many relationship between a Student and ClassQuiz model

class_quiz_score = db.Table('class_quiz_scores',
    db.Column('student_id', db.Integer, db.ForeignKey('student.id'), primary_key=True),
    db.Column('quiz_id', db.Integer, db.ForeignKey('class_quiz.id'), primary_key=True),
    db.Column('scores', db.Integer),
    db.Column('wrong_question_list', db.Text)
)