from server import db

class ClassQuiz(db.Model):
    __tablename__ = 'class_quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(256), nullable=False)
    max_score= db.Column(db.Integer, nullable=False)
    
    # This field is used for storing the weight distributions of questions
    question_weights = db.Column(db.Integer, nullable=False)

    class_id = db.Column(db.Integer, db.ForeignKey('school_class.id'), nullable=False)
    
    # This field is used to store the selected quiz questions from the Question database
    questions_list = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<ClassQuiz %r>' % self.name