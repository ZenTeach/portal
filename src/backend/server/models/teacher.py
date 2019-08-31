from server import db

class Teacher(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    date_of_birth = db.Column(db.DateTime, nullable=False)
    
    classes = db.relationship('SchoolClass', backref='teacher', lazy=True)

    def __repr__(self):
        return '<Teacher %r>' % self.name

    def full_name(self):
        return "{} {}".format(self.firstname, self.lastname)
