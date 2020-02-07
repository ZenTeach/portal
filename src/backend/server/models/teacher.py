from server import db
from server.models.base_model import BaseModelMixin
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID

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

    def __repr__(self):
        return '<Teacher %r>' % self.id

    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def owns_class(self, class_id):
        """
            Checks if the teacher owns the class
        """

        if class_id is None:
            return False

        return class_id in self.classes
