from server import db
from server.models.base_model import BaseModelMixin


class ClassQuiz(BaseModelMixin, db.Model):
    __tablename__ = 'class_quiz'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject = db.Column(db.String(256), nullable=False)
    max_score = db.Column(db.Integer, nullable=False)

    question_weights = db.Column(db.Integer, nullable=False)

    class_id = db.Column(db.Integer, db.ForeignKey(
        'school_class.id'), nullable=False)

    questions_list = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return '<ClassQuiz %r>' % self.name

    def to_json(self):
        return {
            'subject': self.subject,
            'max_score': self.max_score,
            'questions_list': self.questions_list
        }
