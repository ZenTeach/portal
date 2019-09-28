from server import db
from server.models.base_model import BaseModelMixin


class Teacher(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
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

    @property
    def filterable_columns(self):
        return ["password"]
