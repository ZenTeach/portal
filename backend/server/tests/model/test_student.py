from typing import Dict, List

import pytest
from factory import build
from flask.testing import FlaskClient
from server.models import (ClassQuiz, SchoolClass, Student,
                           StudentAttendedClass, Teacher)
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def student_() -> Dict:
    return build(dict, FACTORY_CLASS=StudentFactory)


@pytest.fixture
def student() -> Student:
    return StudentFactory()


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def classrooms_(teacher_: Teacher) -> List[SchoolClass]:
    return SchoolClassFactory.create_batch(5, teacher_id=teacher_.id)


@pytest.fixture
def classroom_(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


def test_student_model_is_saved(client: FlaskClient, student_: Student) -> None:
    st = Student(**student_)
    st.save()

    assert st.id is not None
    assert st.firstname == student_['firstname']
    assert st.lastname == student_['lastname']
    assert st.password is not None
    assert st.email == student_['email']
    assert st.role == "Student"


def test_student_add_to_class(client: FlaskClient,
                              student_: Student,
                              classroom_: ClassQuiz) -> None:
    st = Student(**student_)
    st.save()

    st.add_to_class(classroom_)

    assert len(st.classes) != 0
    assert st.classes[0] == classroom_


def test_student_save_with_class(client: FlaskClient,
                                 student_: Student,
                                 classroom_: ClassQuiz) -> None:
    st = Student(**student_)
    st.save()

    st.add_to_class(classroom_)

    assert st.id is not None
    assert st.classes[0] == classroom_


def test_student_class_remove(client: FlaskClient,
                              student_: Student,
                              classroom_: SchoolClass) -> None:
    st = Student(**student_)
    st.save()

    st.add_to_class(classroom_)
    assert len(st.classes) > 0

    st.remove_class(classroom_)
    assert st.classes == []


def test_student_class_append(client: FlaskClient,
                              student_: Student,
                              classrooms_: List[SchoolClass],
                              classroom_: SchoolClass) -> None:
    st = Student(**student_, classes=classrooms_)
    st.save()

    st.add_from_class_list(classrooms_)

    assert len(st.classes) == 5

    st.classes.append(classroom_)

    assert len(st.classes) == 6


def test_student_remove(client: FlaskClient,
                        student_: Student,
                        classrooms_: ClassQuiz) -> None:
    st = Student(**student_)
    st.save()
    st.add_from_class_list(classrooms_)

    assert Student.query.count() == 1
    assert StudentAttendedClass.query.filter_by(student_id=st.id).count() == 5

    Student.remove_model(st)
    assert StudentAttendedClass.query.filter_by(student_id=st.id).count() == 0


def test_student_update_email(client: FlaskClient,
                              student: Student) -> None:
    student.update_email("test@example.com")
    student.reload()

    assert student.email == "test@example.com"

    student.update_email("")
    student.reload()
    assert student.email == "test@example.com"
