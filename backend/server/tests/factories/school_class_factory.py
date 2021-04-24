from random import choice, randint

from factory import RelatedFactoryList, Trait, post_generation
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import ClassQuizStatus, SchoolClass
from server.tests.factories import ClassQuizFactory

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)


class SchoolClassFactory(SQLAlchemyModelFactory):
    class Meta:
        model = SchoolClass
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    class Params:
        with_students = Trait(
            students=RelatedFactoryList(
                "server.tests.factories.StudentFactory",
                size=lambda: randint(5, 10)
            )
        )

    name = fake.sentence(
        nb_words=3, variable_nb_words=True, ext_word_list=None)
    subject = ""
    start_date = fake.date_time_between(
        start_date="-1y", end_date="now", tzinfo=None)
    year_group = choice(["Year 7", "Year 8", "Year 9", "Year 10", "Year 11", "Year 12", "Year 13"])
    exam_board = choice(['aqa', 'ocr_gateway'])

    @post_generation
    def with_classquiz(obj, create, extracted, **kwargs):
        if create:
            status = extracted

            if not isinstance(extracted, ClassQuizStatus):
                status = ClassQuizStatus.created

            ClassQuizFactory(class_id=obj.id, with_multiple_choice_questions=4, status=status)
