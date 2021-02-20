from json import dumps
from os import getenv
from pathlib import Path
from typing import Dict, Union
from uuid import uuid4

import pytest
from flask.testing import FlaskClient
from pytest_mock import MockFixture
from server.lib import ReportCardGenerator
from server.lib.generators.report_card_generator import (ModelNotFound,
                                                         highlight_progress,
                                                         parse_json_blob,
                                                         render_quill_delta)
from server.models import ClassQuiz, QuizGrade, SchoolClass, Student, Teacher
from server.tests.factories import (ClassQuizFactory, QuizGradeFactory,
                                    SchoolClassFactory, StudentFactory,
                                    TeacherFactory)


@pytest.fixture
def teacher_() -> Teacher:
    return TeacherFactory.create()


@pytest.fixture
def school_class(teacher_: Teacher) -> SchoolClass:
    return SchoolClassFactory.create(teacher_id=teacher_.id)


@pytest.fixture
def student(school_class: SchoolClass) -> Student:
    student = StudentFactory()
    school_class.add_student(student)
    return student


@pytest.fixture
def classquiz_(school_class: SchoolClass) -> ClassQuiz:
    cq = ClassQuizFactory.build(class_id=school_class.id)
    cq.save()
    return cq


@pytest.fixture
def quiz_grade(student: Student, classquiz_: ClassQuiz) -> QuizGrade:
    return QuizGradeFactory(student_id=student.id,
                            class_quiz_id=classquiz_.id, graded=True, score=None)


def test_report_card_generator_init(mocker: MockFixture) -> None:
    def __mock_init(*args):
        assert len(args) == 4

    mocker.patch('server.lib.ReportCardGenerator.__init__', __mock_init)
    ReportCardGenerator("templates", "report_card_template.html", "output")


def test_report_card_generate(client: FlaskClient,
                              mocker: MockFixture,
                              file_fixture_dir: str,
                              quiz_grade: QuizGrade) -> None:
    generator = ReportCardGenerator(
        file_fixture_dir, "dummy_report_card_template.html", getenv("TMP_DIR"))

    generator.generate(quiz_grade.uuid)
    assert Path(getenv("TMP_DIR")).joinpath(f"Report_card_{quiz_grade.uuid}.pdf").exists()


def test_report_card_check_directory_exception(client: FlaskClient,
                                               mocker: MockFixture,
                                               file_fixture_dir: str,
                                               quiz_grade: QuizGrade) -> None:

    generator = ReportCardGenerator("", "dummy_report_card_template.html", getenv("TMP_DIR"))

    with pytest.raises(OSError):
        generator.generate(quiz_grade.uuid)


def test_report_card_quiz_grade_does_not_exist(client: FlaskClient,
                                               file_fixture_dir: str,) -> None:

    generator = ReportCardGenerator(
        file_fixture_dir, "dummy_report_card_template.html", getenv("TMP_DIR"))

    with pytest.raises(ModelNotFound):
        generator.generate(uuid4())


def test_report_card_exception_when_generating(client: FlaskClient,
                                               mocker: MockFixture,
                                               file_fixture_dir: str,
                                               quiz_grade: QuizGrade) -> None:

    def _mock_write_pdf(*args, **kwargs):
        raise Exception
    mocker.patch('weasyprint.HTML.write_pdf', _mock_write_pdf)
    generator = ReportCardGenerator(
        file_fixture_dir, "dummy_report_card_template.html", getenv("TMP_DIR"))

    with pytest.raises(Exception):
        generator.generate(quiz_grade.uuid)


@pytest.mark.parametrize('progress_value,expected_value', [
    pytest.param('1/1', 'green'),
    pytest.param('1/2', 'yellow'),
    pytest.param('3/4', 'yellow'),
    pytest.param('0/4', 'red'),
    pytest.param('0/0', ''),
    pytest.param('2/0', ''),
])
def test_report_card_highlight_progress(progress_value: str, expected_value: str):
    assert highlight_progress(progress_value) == expected_value


@pytest.mark.parametrize('feedback_value,return_value', [
    pytest.param('', ''),
    pytest.param(dumps({'a': 'b'}), {'a': 'b'}),
])
def test_report_card_parse_json_blob(feedback_value: str, return_value: Union[Dict, str]) -> None:
    assert parse_json_blob(feedback_value) == return_value


@pytest.mark.parametrize('parsed_data,text_output', [
    pytest.param('Some text', 'Some text'),
    pytest.param([{
        'insert': "Carbon dioxide only makes up 0.04% of the atmosphere.\nEarth's atmosphere is composed of 78% nitrogen, 21% oxygen, 1% argon and 0.04% carbon dioxide.\n"  # noqa
    }],
        "Carbon dioxide only makes up 0.04% of the atmosphere.Earth's atmosphere is composed of 78% nitrogen, 21% oxygen, 1% argon and 0.04% carbon dioxide.")  # noqa
])
def test_report_card_render_quill_delta(parsed_data: Union[Dict, str], text_output: str) -> None:
    # import pdb; pdb.set_trace()
    assert render_quill_delta(parsed_data) == text_output
