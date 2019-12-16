from .questions import question_seeds
from server import bcrypt
from server.models import Teacher, SchoolClass, Student, StudentAttendedClass
import datetime
from uuid import uuid4

def seeds():
    # Teacher seed
    password = bcrypt.generate_password_hash('Asdfgh12!')
    Teacher(firstname="john", lastname="doe", email="connect@ngetahun.me", date_of_birth="01-01-1970",
            password=password.decode('utf-8'), role="Teacher", uuid=uuid4()).save()
    # Admin Teacher seed
    Teacher(firstname="jane", lastname="doe", email="john.doe+2@example.com", date_of_birth="04-04-1975",
            password=password.decode('utf-8'), role="Admin", uuid=uuid4()).save()

    # Student
    Student(firstname="peter", lastname="griffin", date_of_birth="01-01-2002",
            email="peter.griffin@example.com", password=password.decode('utf-8'), role="Student", uuid=uuid4()).save()

    # SchoolClass
    class_student = Student.query.first()
    class_teacher_id = Teacher.query.filter_by(role="Teacher").first().id
    s = SchoolClass(name="Atoms", subject="Chemistry", start_date=datetime.date.today(
    ), teacher_id=class_teacher_id, uuid=uuid4())

    # interim = StudentAttendedClass()
    # interim.school_class_association = s
    # interim.student_association = class_student
    s.add_student(class_student)
    s.save()


def run_seed():
    seeds()
    question_seeds()
