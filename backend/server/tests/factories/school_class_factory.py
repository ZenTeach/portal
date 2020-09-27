from random import randint

from factory import (RelatedFactory, RelatedFactoryList, SelfAttribute,
                     Sequence, Trait)
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import SchoolClass

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

    id = Sequence(lambda n: n)

    class Params:
        with_students = Trait(
            students=RelatedFactoryList(
                "server.tests.factories.StudentFactory",
                size=lambda: randint(5, 10)
            )
        )
        with_classquiz = Trait(
            class_quiz=RelatedFactory(
                "server.tests.factories.ClassQuizFactory",
                "school_class",
                class_id=SelfAttribute("..id"),
            )
        )

    name = fake.sentence(
        nb_words=3, variable_nb_words=True, ext_word_list=None)
    subject = ""
    start_date = fake.date_time_between(
        start_date="-1y", end_date="now", tzinfo=None)
