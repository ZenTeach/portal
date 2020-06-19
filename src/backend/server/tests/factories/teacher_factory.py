import logging

from factory import RelatedFactory, Trait
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, person
from server import db
from server.models import Teacher

logger = logging.getLogger("factory")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)


class TeacherFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Teacher
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    class Params:
        with_school_class = Trait(
            school_class=RelatedFactory(
                "server.tests.factories.SchoolClassFactory")
        )
        has_class_and_student = Trait(
            school_class=RelatedFactory(
                "server.tests.factories.SchoolClassFactory", with_students=True
            )
        )
        has_class_and_student = Trait(
            school_class=RelatedFactory(
                "server.tests.factories.SchoolClassFactory",
                with_students=True,
                with_classquiz=True,
            )
        )

    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.safe_email()
    password = fake.password(
        length=12,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True
    )
    date_of_birth = fake.date_of_birth()
    role = "Teacher"
