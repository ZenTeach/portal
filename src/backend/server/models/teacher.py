import random
import string
from typing import Optional
from uuid import uuid4

from server import bcrypt, db
from server.models.base_model import BaseModelMixin
from server.models.user_account.confirmable import Confirmable
from server.models.user_account.recoverable import Recoverable
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID


# TODO: Find an alternative to generate human readable password
def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))  # nosec


def unique_uuid4(x: Optional[UUID] = None) -> UUID:
    if x is None:
        x = uuid4()
    return x


class Teacher(BaseModelMixin, db.Model, Confirmable, Recoverable):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship("SchoolClass", backref="teacher", lazy=True)

    confirmed = db.Column(db.Boolean, nullable=True, default=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    confirmation_token = db.Column(db.String, nullable=True)

    recovery_token = db.Column(db.String, nullable=True)
    recovered_at = db.Column(db.DateTime, nullable=True)

    def __init__(
        self,
        firstname,
        lastname,
        email,
        date_of_birth,
        classes=[],
        password=None,
        role="Teacher",
        uuid=None
    ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        if password is None:
            self.password = bcrypt.generate_password_hash(randomString())
        else:
            self.password = bcrypt.generate_password_hash(
                password).decode("utf-8")
        self.role = role

        if self.uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid

        self.classes = classes
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return "%s %s" % (self.firstname, self.lastname)

    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def owns_class(self, class_id):
        """
            Checks if the teacher owns the class
        """

        if class_id is None:
            return False

        return class_id in self.classes

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


@event.listens_for(Teacher.classes, "append")
def teacher_class_append_listener(target, value, initiator):
    value.teacher_id = target.id
    value.save()


@event.listens_for(Teacher.classes, "remove")
def student_class_remove_listener(target, value, initiator):
    db.engine.execute(
        "UPDATE school_class SET teacher_id=null WHERE id=%s", value.id)
