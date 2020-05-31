from server import db
from server.models import QuestionChoice

from factory import SubFactory, RelatedFactory, RelatedFactoryList, post_generation
from factory.alchemy import SQLAlchemyModelFactory
from random import randrange, choice, randint
from uuid import uuid4
from faker import Faker
from faker.providers import internet, date_time, lorem, misc

fake = Faker()
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)

class QuestionChoiceFactory(SQLAlchemyModelFactory):
    class Meta:
        model = QuestionChoice
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'
    weight = randint(1, 10)
    value = fake.sentence()
    feedback = fake.sentence()

    @post_generation
    def question(obj, create, extracted, **kwargs):
      if not create:
        return
      print("Question data", extracted)
      obj.question_id = extracted

    @post_generation
    def is_correct_choice(obj, create, extracted, **kwargs):
        if not create:
            return
        print("Is correct choice data", extracted)
        obj.referenced_question = extracted
