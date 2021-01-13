from random import choice

from factory import Trait
from factory.alchemy import SQLAlchemyModelFactory
from factory.helpers import post_generation
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import Questions, QuestionTypeEnum
from server.tests.factories.question_choice_factory import \
    QuestionChoiceFactory

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
        )
    question = fake.sentence()
    knowledge_item = fake.words()
    tag = fake.words()
    topic = fake.word()
    correct_choice_id = choice([1, 2, 3, 4])
    subject = choice(["Chemistry", "Biology", "Physics"])

    @post_generation
    def with_choices(obj, create, extracted, **kwargs):
        if create:
            choice_count = extracted or 4
            choice_weight = kwargs.get('weight', 1)
            QuestionChoiceFactory.create_batch(choice_count, question=obj.id, weight=choice_weight)
