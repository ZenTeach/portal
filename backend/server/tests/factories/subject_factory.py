
from random import choice

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import Subject

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class SubjectFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Subject
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    name = choice(['Biology', 'Chemistry', 'Physics'])
    enabled = True
