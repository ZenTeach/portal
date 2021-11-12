from typing import List, Optional
from uuid import uuid4

from server import db
from server.models.base_model import BaseModelMixin
from sqlalchemy.dialects.postgresql import UUID

from .base_model import unique_uuid4


class QuestionChoice(db.Model, BaseModelMixin):
    _IGNORED_COLUMNS = ["uuid", "id"]

    __tablename__ = "question_choice"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    value = db.Column(db.String(256), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=0)
    user_created = db.Column(db.Boolean, nullable=True, default=False)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), nullable=True)

    feedback = db.Column(db.Text, nullable=True, default="")
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())

    def __init__(self,
                 value: str,
                 feedback: str,
                 weight: int = 0,
                 uuid: Optional[UUID] = None,
                 question_id: Optional[int] = None,
                 teacher_id: Optional[int] = None,
                 user_created: Optional[bool] = False):
        self.value = value
        self.weight = weight
        if uuid is None:
            self.uuid = unique_uuid4()
        self.feedback = feedback
        if question_id is not None:
            self.question_id = question_id
        self.user_created = user_created
        self.teacher_id = teacher_id

    @property
    def is_correct_choice(self):
        if not hasattr(self, "_is_correct_choice"):
            self._is_correct_choice = False

        return self._is_correct_choice

    @is_correct_choice.setter
    def is_correct_choice(self, val):
        self._is_correct_choice = val

    def __repr__(self):
        return "Choice: {}".format(self.value)

    def get_non_pk_columns(self) -> List[str]:
        table = self.__table__
        return [k for k in table.columns.keys() if k not in table.primary_key and k not in self._IGNORED_COLUMNS]  # noqa

    @classmethod
    def empty_instance(cls):
        return cls(value="", feedback="")

    @classmethod
    def clone(cls, instance: 'QuestionChoice', autosave=False, **kwargs: dict) -> 'QuestionChoice':
        instance.id

        non_pk_columns = instance.get_non_pk_columns()
        data = {c: getattr(instance, c) for c in non_pk_columns}
        data.update(kwargs)

        clone = instance.__class__(**data)
        try:
            if autosave:
                clone.save()
        except Exception as e:
            raise e

        return clone
