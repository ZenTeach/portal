from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import Topic

fake = Faker()
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class TopicFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Topic
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    value = fake.word()
