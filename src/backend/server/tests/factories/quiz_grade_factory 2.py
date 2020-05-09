from server import db
from server.models import QuizGrade

from factory.alchemy import SQLAlchemyModelFactory
from factory import SubFactory, RelatedFactory
from faker import Faker
from faker.providers import person, internet, date_time, lorem, misc
from uuid import uuid4
from random import randrange
import logging

logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)

class QuizGradeFactory(SQLAlchemyModelFactory):
    class Meta:
        model = QuizGrade
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    uuid = uuid4()
    student_id = RelatedFactory('server.tests.factories.StudentFactory')
    class_quiz_id = RelatedFactory('server.tests.factories.ClassQuizFactory')
    student = SubFactory('server.tests.factories.StudentFactory')
    class_quiz = SubFactory('server.tests.factories.ClassQuizFactory')
    score = randrange(5,9)
    grade_breakdown = {}
    responses = {}
