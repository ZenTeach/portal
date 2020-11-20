from typing import List

import pytest
from factory import build
from server import db
from server.models import SchoolClass, Student, StudentAttendedClass, Teacher
from server.tests.factories import (SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def student_():
    return build(dict, FACTORY_CLASS=StudentFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def classrooms_(teacher_) -> List[SchoolClass]:
    return SchoolClassFactory.create_batch(5, teacher_id=teacher_.id)


@pytest.fixture
def classroom_(teacher_) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


def test_student_model_is_saved(client, student_):
    st = Student(**student_)
    st.save()

    assert st.id is not None
    assert st.firstname == student_['firstname']
    assert st.lastname == student_['lastname']
    assert st.password is not None
    assert st.email == student_['email']
    assert st.role == "Student"


@pytest.mark.skip
def test_student_save_with_class(client, student_, classrooms_):
    st = Student(**student_, classes=classrooms_)
    st.save()

    assert st.id is not None
    assert st.classes == classrooms_


@pytest.mark.skip
def test_student_class_remove(client, student_, classroom_):
    st = Student(**student_, classes=[classroom_])
    st.save()

    del st.classes[0]

    assert st.id is not None
    assert st.classes == []


@pytest.mark.skip("Skipped until fixing primary key contraints for student_attended_class")
def test_student_class_append(client, student_, classrooms_, classroom_):
    st = Student(**student_, classes=classrooms_)
    st.save()

    assert len(st.classes) == 5

    st.classes.append(classroom_)

    assert len(st.classes) == 6


@pytest.mark.skip("Skipped until fixing primary key contraints for student_attended_class")
def test_student_remove(client, student_, classrooms_):
    st = Student(**student_, classes=classrooms_)
    # st.save()
    db.session.refresh(st)

    assert StudentAttendedClass.query.filter_by(student_id=st.id).count() == 5

    assert StudentAttendedClass.query.filter_by(student_id=st.id).count() == 0
