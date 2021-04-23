import datetime
from random import choice
from uuid import uuid4

from flask_bcrypt import generate_password_hash
from server.models import Admin, SchoolClass, Student, Subject, Teacher

from .questions import question_seeds


def seeds():
    # Teacher seed
    password = "Asdfgh12!"  # nosec
    Teacher(
        firstname="john",
        lastname="doe",
        email="connect@ngetahun.me",
        date_of_birth="01-01-1970",
        password=password,
        role="Teacher",
        uuid=uuid4(),
    ).save()
    # Admin Teacher seed
    Admin(
        firstname="jane",
        lastname="doe",
        email="john.doe+2@example.com",
        date_of_birth="04-04-1975",
        password=generate_password_hash(password, 12).decode('utf-8'),
        role="Admin",
        uuid=uuid4(),
    ).save()

    # Student
    Student(
        firstname="peter",
        lastname="griffin",
        email="peter.griffin@example.com",
        password=password,
        role="Student",
    ).save()

    # SchoolClass
    class_student = Student.query.first()
    class_teacher_id = Teacher.query.filter_by(role="Teacher").first().id
    s = SchoolClass(
        name="Atoms",
        subject="Chemistry",
        exam_board=None,
        start_date=datetime.date.today(),
        teacher_id=class_teacher_id,
        uuid=uuid4(),
    )

    # classrooms
    for i in range(2, 6):
        ids = Subject.query.with_entities(
            Subject.id
        ).filter(
            Subject.name.in_(
                ['Biology', 'Chemistry', 'Physics']
            )
        ).all()

        SchoolClass(
            name=f"Atoms-{i}",
            subject_id=choice(ids)[0],
            exam_board=None,
            start_date=datetime.date.today(),
            teacher_id=class_teacher_id,
            uuid=uuid4(),
        ).save()

    s.add_student(class_student)


def run_seed():
    add_subjects()
    seeds()
    question_seeds()


def add_subjects():
    subjects = ["Art and Design",
                "Business",
                "Computer Science",
                "Design and Technology",
                "Drama",
                "English Language",
                "English Literature",
                "French",
                "Geography",
                "German",
                "History",
                "ICT",
                "Maths",
                "Media Studies",
                "Music",
                "Physical Education",
                "Religious Studies",
                "Sociology",
                "Spanish",
                "Biology",
                "Chemistry",
                "Physics"
                ]
    for subject in subjects:
        Subject(name=subject, enabled=True).save()
