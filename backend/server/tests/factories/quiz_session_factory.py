from datetime import datetime, timedelta
from uuid import uuid4

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import QuizSession, QuizSessionStatus

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class QuizSessionFactory(SQLAlchemyModelFactory):
    class Meta:
        model = QuizSession
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    uuid = uuid4()
    start_time = datetime.utcnow()
    end_time = datetime.utcnow() + timedelta(hours=1)
    status = QuizSessionStatus.ended
