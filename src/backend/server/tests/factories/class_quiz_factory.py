import logging
from random import choice, randrange

from factory import post_generation
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, misc, person
from server import db
from server.models import ClassQuiz

logger = logging.getLogger("factory")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

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
    max_score = randrange(5, 9)
    variants = randrange(1, 4)
    school_class = None

    @post_generation
    def school_class(obj, create, extracted, **kwargs):
        if not create:
            return
        print("SCHOOL CLASS data", extracted)
        obj.class_id = extracted

    # student_quiz_sessions = RelatedFactoryList(QuizSessionFactory,
    #                           'student_quiz_sessions', size=4)
    # student_quiz_grades = RelatedFactoryList(QuizGradeFactory,
    #                           'student_quiz_sessions', size=4)
    questions = [
        {
            "choices": {
                "a": "The smallest piece of an element that can exist.",
                "b": "A particle that cannot be broken down any further.",
                "c": "Multiple compounds chemically bonded to each other.",
                "d": "A particle that has no mass.",
            },
            "id": 10,
            "knowledge_item": "DEFINITION ATOM",
            "question": "What is an atom?",
            "question_type": 1,
            "subject": "Chemistry",
            "tag": "6",
            "topic": "Atomic Structure",
        },
        {
            "choices": {
                "a": "Matter made of at least two types of atoms.",
                "b": "",
                "c": "Matter that is only made of one type of atom.",
                "d": "",
            },
            "id": 11,
            "knowledge_item": "DEFINITION ELEMENT",
            "question": "What is an element?",
            "question_type": 1,
            "subject": "Chemistry",
            "tag": "7",
            "topic": "Atomic Structure",
        },
        {
            "choices": {
                "a": "Electrons have a mass of 1 and a negative charge.",
                "b": "Electrons have a mass of 0 and a negative charge.",
                "c": "Electrons have a mass of 0 and a positive charge.",
                "d": "Electrons have a mass of 0 and a neutral charge.",
            },
            "id": 6,
            "knowledge_item": "ELECTRON MASS AND CHARGE",
            "question": "Which statements about electrons are correct?",
            "question_type": 1,
            "subject": "Chemistry",
            "tag": "3",
            "topic": "Atomic Structure",
        },
    ]
