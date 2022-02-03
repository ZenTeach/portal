from typing import Optional

from marshmallow import validates
from server import db, ma
from server.models import Teacher
from server.models.base_model import BaseModelMixin

CREATE = 1
UPDATE = 2
DELETE = 3


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

    # Note
    note = db.Column(db.Text, nullable=True)

    # TODO: Remove this after moving to TimeStampMixin
    created = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated = db.Column(db.DateTime, nullable=False, server_default=db.func.now())

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


class ActivityLogSchema(ma.ModelSchema):
    class Meta:
        model = ActivityLog
        load_instance = True
        fields = ('actor_id', 'note', 'action',
                  'item_type', 'item_id')

    @validates('item_type')
    def validate_item_type(self, item_type: str) -> bool:
        return item_type in [
            'teacher', 'class_quiz', 'invitations',
            'topic', 'subject', 'question_choice',
            'knowledge_item', 'questions', 'school_class',
            'student_attended_class']

    @validates('actor_id')
    def validate_teacher_id(self, id: int) -> bool:
        return Teacher.query.filter_by(id=id).count() > 0

    @validates('item_id')
    def validate_item_id(self, _item_id: str) -> bool:
        # TODO: Fix this. Implement database consistence check.
        pass
