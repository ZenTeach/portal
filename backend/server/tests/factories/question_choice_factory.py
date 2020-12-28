from random import choice

from factory import post_generation
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import QuestionChoice

fake = Faker()
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class QuestionChoiceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = QuestionChoice
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    weight = choice([1, 0, 0, 0])
    value = fake.sentence()
    feedback = fake.sentence()

    @post_generation
    def question(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.question_id = extracted
