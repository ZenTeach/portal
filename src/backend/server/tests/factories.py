from factory import Factory, SubFactory, Iterator, post_generation, RelatedFactory, PostGenerationMethodCall, RelatedFactoryList
from factory.alchemy import SQLAlchemyModelFactory
from server.models import Teacher, Student, SchoolClass, ClassQuiz, ClassQuizStatus
from server import db

from faker import Faker
from faker.providers import person, internet, date_time, lorem, misc
from random import randrange, choice, randint

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
    # @post_generation
    # # def post(self, create, extracted, **kwargs):
    # #     print("POST data", extracted)
    # #     self.class_id = extracted
    questions = [
       {
            "question_id": 2,
            "is_edited": False,
            "edited_question": "",
            "question_choices": [
                {
                    "choice_id": 2,
                    "is_edited": False,
                    "edited_choice": "",
                    "choice_weight": 0,
                    "feedback": ""
                },
                {
                    "choice_id": 3,
                    "is_edited": False,
                    "edited_choice": "",
                    "choice_weight": 1,
                    "feedback": ""
                },
                {
                    "choice_id": 5,
                    "is_edited": False,
                    "edited_choice": "",
                    "choice_weight": 0,
                    "feedback": ""
                },
                {
                    "choice_id": 7,
                    "is_edited": False,
                    "edited_choice": "",
                    "choice_weight": 0,
                    "feedback": ""
                }]
        }
    ]

class ClassQuizScoreFactory(BaseSQLAlchemyModelFactory):
    class Meta:
        inline_args = ('student_id', 'quiz_id', 'scores', 'wrong_question_list')

    scores = randrange(1, 9)
    wrong_question_list = ', '.join([str(randrange(1, 9)) for i in range(7)])
    student_id = RelatedFactory(StudentFactory, 'id')
    quiz_id = RelatedFactory(ClassQuizFactory, 'id')

