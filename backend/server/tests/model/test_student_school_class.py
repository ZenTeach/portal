
from typing import List

import pytest
from flask.testing import FlaskClient
from server.models import SchoolClass, Student, Teacher
from server.models.student_school_class import StudentAttendedClass
from server.tests.factories import SchoolClassFactory, StudentFactory


@pytest.fixture
def student_(client: FlaskClient) -> Student:
    return StudentFactory.create()


@pytest.fixture
def students_(client: FlaskClient) -> List[Student]:
    return StudentFactory.create_batch(6)


@pytest.fixture
def teacher_() -> Teacher:
    return Teacher.query.first()


@pytest.fixture
def classroom_(teacher_) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def classrooms_(teacher_) -> List[SchoolClass]:
    return SchoolClassFactory.create_batch(5, teacher_id=teacher_.id)


def test_student_school_class_saved(client, student_, classroom_):
    obj = StudentAttendedClass(student_, classroom_)
    obj.save()

    assert obj.student_id == student_.id
    assert obj.school_class_id == classroom_.id


def test_student_with_multiple_classes(client, student_, classrooms_):
    for _class in classrooms_:
        obj = StudentAttendedClass(student_, _class)
        obj.save()

    assert student_.classes == classrooms_


def test_school_class_with_multiple_students(client, classroom_, students_):
    for student in students_:
        obj = StudentAttendedClass(student, classroom_)
        obj.save()

    assert classroom_.students == students_


def test_student_attended_class_deletion(client, student_: 'Student', classrooms_):
    for class_ in classrooms_:
        student_.add_to_class(class_)

    [_sac.delete() for _sac in StudentAttendedClass.query.filter_by(student_id=student_.id).all()]

    assert StudentAttendedClass.query.filter_by(student_id=student_.id).count() == 0
