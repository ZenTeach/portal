import datetime
from uuid import uuid4

from server.models import Admin, SchoolClass, Student, Teacher

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
        password=password,
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
        start_date=datetime.date.today(),
        teacher_id=class_teacher_id,
        uuid=uuid4(),
    )

    # interim = StudentAttendedClass()
    # interim.school_class_association = s
    # interim.student_association = class_student

    # Add Quiz
    # _class = SchoolClass.query.first()

    # ClassQuizModel(subject=_class.subject,
    #                 max_score=3,
    #                 class_id=_class.id,
    #                 variants=3,
    #                 questions=)
    s.add_student(class_student)
    s.save()


def run_seed():
    seeds()
    question_seeds()
