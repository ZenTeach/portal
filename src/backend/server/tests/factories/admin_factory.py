
from uuid import uuid4

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, person
from server import bcrypt, db
from server.models import Admin

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)


class AdminFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Admin
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"
    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.safe_email()
    date_of_birth = "04-04-1975"
    password = bcrypt.generate_password_hash("Asdfgh12!")
    role = "Admin"
    uuid = uuid4()
