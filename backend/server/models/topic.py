from flask_babel import get_locale
from flask_sqlalchemy import BaseQuery
from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils import TranslationHybrid
from sqlalchemy_utils.types import TSVectorType


class TopicsQuery(BaseQuery, SearchQueryMixin):
    pass


translation_hybrid = TranslationHybrid(
    current_locale=get_locale,
    default_locale="en"
)


class Topic(db.Model, BaseModelMixin):
    __tablename__ = "topics"
    query_class = TopicsQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    value = db.Column(db.String(255), nullable=False)
    value_translations = db.Column(HSTORE, nullable=False)
    topic_value = translation_hybrid(value_translations)

    # relationships
    questions = db.relationship("Questions", lazy='dynamic')
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship("Subject", lazy='joined', uselist=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.id"), nullable=True)
    teacher = db.relationship("Teacher", lazy='joined', uselist=False)
    knowledge_items = db.relationship("KnowledgeItem", lazy='dynamic')
    search_vector = db.Column(TSVectorType("value"))

    def __repr__(self):
        return f"{self.value}"

    @hybrid_property
    def linked_question_count(self):
        return self.questions.count()
