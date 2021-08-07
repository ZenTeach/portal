from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import KnowledgeItem

fake = Faker()
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class KnowledgeItemFactory(SQLAlchemyModelFactory):
    class Meta:
        model = KnowledgeItem
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    value = fake.word()
