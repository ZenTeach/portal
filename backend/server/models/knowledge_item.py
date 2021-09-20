from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy import event
from sqlalchemy.ext.hybrid import hybrid_property


class KnowledgeItem(db.Model, BaseModelMixin):
    __tablename__ = 'knowledge_items'

    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(255), nullable=False)
    questions = db.relationship("Questions", lazy='dynamic', viewonly=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship("Subject", lazy='joined', uselist=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=True)
    teacher = db.relationship("Teacher", lazy='joined', uselist=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topics.id"), nullable=True)
    topic = db.relationship("Topic", lazy='joined', uselist=False, viewonly=True)

    def __repr__(self):
        return f"{self.value}"

    @hybrid_property
    def linked_question_count(self):
        return self.questions.count()

    def add_to_questions(self, question):
        self.questions.append(question)
        self.save()


@event.listens_for(KnowledgeItem.questions, "remove")
def knowledge_item_questions_remove_listener(target, value, initiator):
    db.engine.execute(
        "UPDATE questions SET _knowledge_item_id=null WHERE id=%s", value.id)


@event.listens_for(KnowledgeItem.questions, "append")
def question_knowledge_item_append_listener(target, value, initiator):
    value._knowledge_item_id = target.id
    value.save()


@event.listens_for(KnowledgeItem.topic, 'set')
def question_topic_set_listener(target, value, _oldvalue, _initiator):
    if value is not None:
        target.topic_id = value.id
        target.save()
    else:
        target.topic_id = None
        target.save()
