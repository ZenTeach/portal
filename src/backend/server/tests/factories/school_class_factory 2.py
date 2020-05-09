from server import db
from server.models import SchoolClass
from factory import RelatedFactory, RelatedFactoryList, post_generation

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import person, internet, date_time, lorem, misc
import logging
logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

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
        sqlalchemy_session_persistence = 'commit'

    name = fake.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)
    subject = ''
    start_date = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)

    teacher_id = RelatedFactory('server.tests.factories.TeacherFactory')
    #student_id = RelatedFactory('server.tests.factories.StudentFactory')

    # @post_generation
    # def post(self, create, extracted, **kwargs):
    #     self.quizzes.append(ClassQuizFactory.create(post=self.id))
    @post_generation
    def teacher(self, create, extracted, **kwargs):
      if create:
        return
      self.teacher_id = extracted
    students = RelatedFactoryList('server.tests.factories.StudentFactory', size=lambda: randint(5, 10))
    quizzes = RelatedFactoryList('server.tests.factories.ClassQuizFactory', size=lambda: randint(1,4))
    #quizzes = RelatedFactory(ClassQuizFactory)

