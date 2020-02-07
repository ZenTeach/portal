from factory import Factory, SubFactory, Iterator, post_generation, RelatedFactory, PostGenerationMethodCall, RelatedFactoryList
from factory.alchemy import SQLAlchemyModelFactory
from server.models import Teacher, Student, SchoolClass, ClassQuiz, ClassQuizStatus
from server import db

from faker import Faker
from faker.providers import person, internet, date_time, lorem, misc
from random import randrange, choice, randint
from uuid import uuid4
from flask_jwt_extended import create_access_token

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)
fake.add_provider(misc)

# Taken from: https://stackoverflow.com/questions/48568472/how-can-you-globally-set-sqlalchemy-session-persistence-for-factory-boy-in-only
class BaseSQLAlchemyModelFactory(SQLAlchemyModelFactory):
    """Base Test factory abstract class"""

    class Meta:
        abstract = True
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'


# StudentFactory.create(add_quiz_grades_to_student=ClassQuizScoreFactory.create_batch())
class StudentFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = Student

    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.safe_email()
    password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    date_of_birth = fake.date_of_birth()
    role="Student"
    # classes = RelatedFactory('server.tests.factories.SchoolClassFactory')

    @post_generation
    def add_quiz_grades_to_student(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for quiz in extracted:
                self.quiz_grades.add(quiz)



class TeacherFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = Teacher

    firstname = fake.first_name()
    lastname = fake.last_name()
    email = fake.safe_email()
    password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)
    date_of_birth = fake.date_of_birth()
    role="Teacher"

    @post_generation
    def classes(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for __class in extracted:
                self.classes.add(__class)

class SchoolClassFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = SchoolClass

    name = fake.sentence(nb_words=3, variable_nb_words=True, ext_word_list=None)
    subject = ''
    start_date = fake.date_time_between(start_date="-1y", end_date="now", tzinfo=None)

    teacher_id = RelatedFactory('server.tests.factories.TeacherFactory')
    #student_id = RelatedFactory('server.tests.factories.StudentFactory')

    # @post_generation
    # def post(self, create, extracted, **kwargs):
    #     self.quizzes.append(ClassQuizFactory.create(post=self.id))
    students = RelatedFactoryList(StudentFactory, size=lambda: randint(5, 10))
    #quizzes = RelatedFactoryList(ClassQuizFactory, size=lambda: randint(1,4))


class ClassQuizFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        model = ClassQuiz

    subject = fake.sentence(nb_words=4)
    max_score = randrange(5,9)
    variants = randrange(1,4)
    status = ClassQuizStatus.created
    script_id = None
	id = 1
	school_class = 1
	uuid = uuid4()
    # @post_generation
    # # def post(self, create, extracted, **kwargs):
    # #     print("POST data", extracted)
    # #     self.class_id = extracted
    questions = [{
		'choices': {
			'a': 'The smallest piece of an element that can exist.',
			'b': 'A particle that cannot be broken down any further.',
			'c': 'Multiple compounds chemically bonded to each other.',
			'd': 'A particle that has no mass.'
		},
		'id': 10,
		'knowledge_item': 'DEFINITION ATOM',
		'question': 'What is an atom?',
		'question_type': 1,
		'subject': 'Chemistry',
		'tag': '6',
		'topic': 'Atomic Structure'
	    }, {
		'choices': {
			'a': 'Matter made of at least two types of atoms.',
			'b': '',
			'c': 'Matter that is only made of one type of atom.',
			'd': ''
		},
		'id': 11,
		'knowledge_item': 'DEFINITION ELEMENT',
		'question': 'What is an element?',
		'question_type': 1,
		'subject': 'Chemistry',
		'tag': '7',
		'topic': 'Atomic Structure'
	    }, {
		'choices': {
			'a': 'Electrons have a mass of 1 and a negative charge.',
			'b': 'Electrons have a mass of 0 and a negative charge.',
			'c': 'Electrons have a mass of 0 and a positive charge.',
			'd': 'Electrons have a mass of 0 and a neutral charge.'
		},
		'id': 6,
		'knowledge_item': 'ELECTRON MASS AND CHARGE',
		'question': 'Which statements about electrons are correct?',
		'question_type': 1,
		'subject': 'Chemistry',
		'tag': '3',
		'topic': 'Atomic Structure'
	}]

class ClassQuizScoreFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        inline_args = ('student_id', 'quiz_id', 'scores', '')

    score = randrange(1, 9)
    # wrong_question_list = ', '.join([str(randrange(1, 9)) for i in range(7)])
    student_id = RelatedFactory(StudentFactory, 'id')
    quiz_id = RelatedFactory(ClassQuizFactory, 'id')
    responses = {

    }

    # grade_breakdown = {

    # }

