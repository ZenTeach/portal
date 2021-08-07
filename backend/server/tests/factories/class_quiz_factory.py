from random import choice

from factory import post_generation
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import ClassQuiz, QuestionsSchema
from server.tests.factories.question_factory import QuestionsFactory

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class ClassQuizFactory(SQLAlchemyModelFactory):
    class Meta:
        model = ClassQuiz
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    subject = choice(["Chemistry", "Biology", "Physics"])

    @post_generation
    def with_multiple_choice_questions(obj, create, extracted, **kwargs):
        if create:
            question_count = extracted or 5
            questions = QuestionsFactory.create_batch(question_count,
                                                      multiple_choice_question_type=True,
                                                      with_choices={
                                                          'choice_count': 4
                                                      })
            dumper = QuestionsSchema()
            obj.questions = [dumper.dump(question) for question in questions]
