from typing import Optional

from marshmallow import (Schema, ValidationError, post_load, validates,
                         validates_schema)
from server import db
from server.models import Teacher
from server.models.base_model import BaseModelMixin
from sqlalchemy import MetaData, Table
from sqlalchemy_utils import generic_relationship, get_primary_keys

CREATE = 1
UPDATE = 2
DELETE = 3

LOGGABLE_ITEM_TYPES = [
    'teacher', 'class_quiz', 'invitations',
    'topics', 'subjects', 'question_choice',
    'knowledge_items', 'questions', 'school_class',
    'student_attended_class', 'quiz_session', 'quiz_grade']

SUMMARIZED_ITEM_TYPES = [f'summarize_{item_type}' for item_type in LOGGABLE_ITEM_TYPES]

DB_EXEMPT_LIST = list(set(['quiz_session', 'quiz_grade']).union(set(SUMMARIZED_ITEM_TYPES)))

DB_VALIDATABLE_ITEMS = list(set(LOGGABLE_ITEM_TYPES) - set(DB_EXEMPT_LIST))

# Teacher activity log


class ActivityLog(BaseModelMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Current user
    actor_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    actor = db.relationship('Teacher', backref=db.backref('activity_logs', lazy='dynamic'))

    # Action name
    action = db.Column(db.String(128), nullable=False)

    # Object
    item_type = db.Column(db.String(128), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    item = generic_relationship(item_type, item_id)

    # Note
    note = db.Column(db.Text, nullable=True)

    @classmethod
    def log(cls,
            actor: Teacher,
            action: str,
            item_type: str,
            item_id: int,
            note: Optional[str] = None):

        log = ActivityLogSchema().load({
            'actor_id': actor.id,
            'action': action,
            'item_type': item_type,
            'item_id': item_id,
            'note': note,
        })
        log.save()

    def __repr__(self):
        return f'Log for {self.item_type} by {self.actor_id} \
               performing {self.action}. Note: {self.note}'


class ActivityLogSchema(Schema):
    class Meta:
        model = ActivityLog
        load_instance = True
        fields = ('actor_id', 'note', 'action',
                  'item_type', 'item_id')

    @validates('item_type')
    def validate_item_type(self, item_type: str) -> bool:
        return item_type in LOGGABLE_ITEM_TYPES

    @validates('actor_id')
    def validate_teacher_id(self, id: int) -> bool:
        return Teacher.query.filter_by(id=id).count() > 0

    @validates_schema(pass_original=True)
    def validate_item_id(self, *values, **kwargs) -> bool:
        data = values[0]
        if data['item_type'] not in DB_VALIDATABLE_ITEMS:
            # don't validate if item_type is not in DB_VALIDATABLE_ITEMS
            return True
        if data['action'] in ('create', 'update'):
            item_type = data['item_type']
            item_id = data['item_id']
            # do db level validation
            item_table = Table(item_type, MetaData(), autoload=True, autoload_with=db.get_engine())
            primary_key = get_primary_keys(item_table).popitem()[1]
            res = db.get_engine().execute(
                f'SELECT * FROM { item_type } WHERE {primary_key.name}={item_id}')  # nosec
            if res.rowcount == 0:
                raise ValidationError(f'Item { item_type } with id {item_id} does not exist')
        else:
            pass

    @post_load
    def make_log(self, data, **kwargs):
        return ActivityLog(**data)
