import pytest
from factory import build
from flask.testing import FlaskClient
from server.models import SchoolClass, Student, Teacher
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def student_() -> Student:
    return StudentFactory.create()


@pytest.fixture
def schoolclass_params(client: FlaskClient, teacher_: Teacher) -> dict:
    return build(dict, FACTORY_CLASS=SchoolClassFactory, teacher_id=teacher_.id)


def test_model_is_saved(client: FlaskClient, schoolclass_params: dict):
    class_ = SchoolClass(**schoolclass_params)
    class_.save()

    assert class_.id is not None


def test_school_class_add_student(client: FlaskClient,
                                  student_: Student,
                                  schoolclass_params: dict):
    class_ = SchoolClass(**schoolclass_params)
    class_.save()

    assert len(class_.students) == 0
    class_.add_student(student_)

    assert len(class_.students) == 1


def test_school_class_remove_student(client: FlaskClient,
                                     student_: Student,
                                     schoolclass_params: dict):
    class_ = SchoolClass(**schoolclass_params)
    class_.save()

    class_.add_student(student_)
    assert len(class_.students) == 1

    class_.remove_student(student_.id)
    assert len(class_.students) == 0


def test_school_class_remove_classroom(client: FlaskClient,
                                       student_: Student,
                                       schoolclass_params: dict):
    class_ = SchoolClass(**schoolclass_params)
    class_.save()
    class_.add_student(student_)

    assert SchoolClass.query.count() == 1
    SchoolClass.remove_classroom(class_)
    assert SchoolClass.query.count() == 0


def test_school_class_has_student(client: FlaskClient,
                                  student_: Student,
                                  schoolclass_params: dict):
    class_ = SchoolClass(**schoolclass_params)
    class_.save()

    assert len(class_.students) == 0
    assert class_.students == []

    class_.add_student(student_)

    assert len(class_.students) == 1
    assert class_.students == [student_]
    assert class_.has_student(student_)
