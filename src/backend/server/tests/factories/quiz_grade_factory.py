from random import randrange
from uuid import uuid4

from factory import RelatedFactory, SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import QuizGrade

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
        sqlalchemy_session_persistence = "commit"

    uuid = uuid4()
    student_id = RelatedFactory("server.tests.factories.StudentFactory")
    class_quiz_id = RelatedFactory("server.tests.factories.ClassQuizFactory")
    student = SubFactory("server.tests.factories.StudentFactory")
    class_quiz = SubFactory("server.tests.factories.ClassQuizFactory")
    score = randrange(5, 9)
    grade_breakdown = {}
    responses = {}
