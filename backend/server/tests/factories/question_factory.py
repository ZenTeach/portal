from random import choice

from factory import Trait
from factory.alchemy import SQLAlchemyModelFactory
from factory.helpers import post_generation
from faker import Faker
from faker.providers import date_time, internet, lorem, misc
from server import db
from server.models import Questions
from server.tests.factories.question_choice_factory import \
    QuestionChoiceFactory
from server.tests.factories.topic_factory import TopicFactory

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
            question_type="multiple_choice"
        )
    question = fake.sentence()
    knowledge_item = fake.word()
    exam_board = choice(['aqa', 'edexcel', 'ccea'])
    tag = fake.word()
    topic = fake.word()
    correct_choice_id = choice([1, 2, 3, 4])
    user_created = choice([True, False])

    @post_generation
    def with_choices(obj, create, extracted, **kwargs):
        """
            how to use
            q = QuestionFactory(with_choices={
                    'choice_count': 4,
                    'choice_weight': 1,
                    'knowledge_item': <knowledge_item>})
        """
        if create:
            if isinstance(extracted, dict):
                choice_count = extracted.get('choice_count', 4)
                choice_weight = extracted.get('choice_weight', 1)
                knowledge_item = extracted.get('knowledge_item', None)
                topic = extracted.get('topic', None)
                QuestionChoiceFactory.create_batch(
                    choice_count, question=obj.id, weight=choice_weight)
                if topic is None:
                    topic = TopicFactory(value=fake.word())
                obj._topic = topic
                if knowledge_item is not None:
                    obj._knowledge_item_id = knowledge_item.id
                    obj._knowledge_item = knowledge_item

                obj.save()
