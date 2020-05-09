from server import db
from server.models import Questions, QuestionTypeEnum

from factory import SubFactory, RelatedFactory, RelatedFactoryList, post_generation, Trait
from factory.alchemy import SQLAlchemyModelFactory
from random import randrange, choice, randint
from uuid import uuid4
from faker import Faker
from faker.providers import internet, date_time, lorem, misc
from random import randint
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
            question_type=QuestionTypeEnum.multiple_choice
            # choices=RelatedFactoryList('server.tests.factories.QuestionChoiceFactory', size=lambda: randint(2, 6))
        )

    question = fake.sentence()
    knowledge_item=fake.words()
    tag=fake.words()
    topic=fake.word()
    subject = choice(["Chemistry", "Biology", "Physics"])
