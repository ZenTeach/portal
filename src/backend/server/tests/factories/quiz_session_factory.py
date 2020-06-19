import logging
from datetime import datetime, timedelta
from uuid import uuid4

from factory import RelatedFactory, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import QuizSession, QuizSessionStatus

logger = logging.getLogger("factory")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

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
    student_id = RelatedFactory("server.tests.factories.StudentFactory")
    class_quiz_id = RelatedFactory("server.tests.factories.ClassQuizFactory")
    student = SubFactory("server.tests.factories.StudentFactory")
    class_quiz = SubFactory("server.tests.factories.ClassQuizFactory")
    start_time = datetime.utcnow()
    end_time = timedelta(hours=1)
    status = QuizSessionStatus.ended
