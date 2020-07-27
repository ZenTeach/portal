from random import choice
from uuid import uuid4

from factory import RelatedFactoryList, Trait
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import Questions, QuestionTypeEnum

fake = Faker()
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class QuestionsFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Questions
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    class Params:
        multiple_choice_question_type = Trait(
            question_type=QuestionTypeEnum.multiple_choice,
            choices=RelatedFactoryList('server.tests.factories.QuestionChoiceFactory',
                                       size=4)
        )
    uuid = uuid4()
    question = fake.sentence()
    knowledge_item = fake.words()
    tag = fake.words()
    topic = fake.word()
    correct_choice_id = choice([1, 2, 3, 4])
    subject = choice(["Chemistry", "Biology", "Physics"])
