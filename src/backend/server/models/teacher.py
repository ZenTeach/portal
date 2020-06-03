from server import db, bcrypt
from server.models.base_model import BaseModelMixin
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import event
import string
import random

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class Teacher(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship('SchoolClass', backref='teacher', lazy=True)

    def __init__(self, firstname, lastname, email, date_of_birth, classes=[], password=None, role="Teacher"):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        if password is None:
            self.password = bcrypt.generate_password_hash(randomString())
        else:
            self.password = password
        self.role = role
        print("In __init__, classes: {}", classes)
        self.classes = classes
        self.date_of_birth = date_of_birth

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)

    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def owns_class(self, class_id):
        """
            Checks if the teacher owns the class
        """

        if class_id is None:
            return False

        return class_id in self.classes

@event.listens_for(Teacher.classes, 'append')
def teacher_class_append_listener(target, value, initiator):
    value.teacher_id = target.id
    value.save()

@event.listens_for(Teacher.classes, 'remove')
def student_class_remove_listener(target, value, initiator):
    db.engine.execute("UPDATE school_class SET teacher_id=null WHERE id=%s", value.id)
