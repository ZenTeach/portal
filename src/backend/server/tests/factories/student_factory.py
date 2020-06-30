from server.models import Student
from server import db

from factory import SubFactory, RelatedFactory, post_generation
from faker import Faker
from faker.providers import person, internet, date_time, lorem, misc

from factory.alchemy import SQLAlchemyModelFactory

import logging
logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)

class StudentFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Student
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.safe_email()
    password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    role="Student"
    # classes = RelatedFactory('server.tests.factories.SchoolClassFactory')

    # @post_generation
    # def add_quiz_grades_to_student(self, create, extracted, **kwargs):
    #     if not create:
    #         return
    #     if extracted:
    #         for quiz in extracted:
    #             self.quiz_grades.add(quiz)

