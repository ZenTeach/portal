
# Test activity log tasks
# Populate the database with a teacher,
# a school class, a student, a class quiz,
# a quiz session, and a quiz grade for the student.
# We will create activity log entries for the teacher.
# Next, we test the task that summarizes activity log entries

import datetime

import pytest
from flask.testing import FlaskClient
from freezegun import freeze_time
from pytest_mock import MockFixture
from server.lib import Summarizer
from server.models import ActivityLog, Subject, Teacher
from server.tests.factories import (ClassQuizFactory, KnowledgeItemFactory,
                                    QuestionsFactory, SchoolClassFactory,
                                    SubjectFactory, TopicFactory)


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return Teacher.query.first()

# Daily summarizable logs


@pytest.fixture
def quiz_grade_logs(teacher_: Teacher) -> None:
    classroom = SchoolClassFactory(teacher_id=teacher_.id)
    class_quiz = ClassQuizFactory(class_id=classroom.id)

    for i in range(10):
        ActivityLog.log(
            teacher_,
            'create',
            'quiz_grade',
            class_quiz.id,
            'Quiz graded')

# Weekly summarizable logs


@pytest.fixture
def school_class_logs(teacher_: Teacher) -> None:
    for i in range(10):
        class_ = SchoolClassFactory.create(teacher_id=teacher_.id)
        ActivityLog.log(teacher_, 'create', class_.__tablename__, class_.id, '')
    teacher_.reload()


@pytest.fixture
def subject_() -> Subject:
    return SubjectFactory()


# Monthly summarizable logs
@pytest.fixture
def uc_question_logs(teacher_: Teacher, subject_: Subject) -> None:
    topic = TopicFactory(value="testKI", subject_id=subject_.id)
    ki = KnowledgeItemFactory(subject_id=subject_.id, topic_id=topic.id)
    for i in range(10):
        q = QuestionsFactory(
            teacher_id=teacher_.id,
            subject_id=subject_.id,
            knowledge_item=ki,
            topic=topic,
            multiple_choice_question_type=True,
            user_created=True,
            with_choices={
                'choice_count': 4,
                'choice_weight': 1})

        ActivityLog.log(
            teacher_,
            'create',
            'questions',
            q.id,
            'Created new question')


@pytest.fixture(scope='function')
def summarizer_instance(teacher_: Teacher) -> None:
    s = Summarizer(teacher_)
    yield s
    del s


class TestSummarizer:
    def test_get_logs_by_temporal_grouping_by_month(self,
                                                    teacher_: Teacher,
                                                    mocker: MockFixture,
                                                    uc_question_logs,
                                                    summarizer_instance) -> None:
        one_month_later = datetime.datetime.now() + datetime.timedelta(days=30)
        mocker.patch('server.lib.Summarizer.generate_human_friendly_summary', return_value=None)
        summarizer_instance = Summarizer(teacher_)
        with freeze_time(one_month_later):
            summarizer_instance(30)
            logs = summarizer_instance.processed_logs
            assert len(logs) == 10

    def test_get_logs_by_temporal_grouping_by_week(self,
                                                   teacher_: Teacher,
                                                   school_class_logs,
                                                   mocker: MockFixture,
                                                   summarizer_instance) -> None:
        one_week_later = datetime.datetime.now() + datetime.timedelta(days=7)
        mocker.patch('server.lib.Summarizer.generate_human_friendly_summary', return_value=None)
        with freeze_time(one_week_later):
            summarizer_instance(7)
            logs = summarizer_instance.processed_logs
            assert len(logs) == 10

    def test_get_logs_by_temporal_grouping_by_day(self,
                                                  teacher_: Teacher,
                                                  quiz_grade_logs,
                                                  mocker: MockFixture,
                                                  summarizer_instance) -> None:
        one_day_later = datetime.datetime.now() + datetime.timedelta(days=1)
        mocker.patch('server.lib.Summarizer.generate_human_friendly_summary', return_value=None)
        with freeze_time(one_day_later):
            summarizer_instance(1)
            logs = summarizer_instance.processed_logs
            assert len(logs) == 10

    @pytest.mark.skip(msg="Re-evaluating purpose")
    def test_get_logs_by_temporal_grouping_exception(self,
                                                     teacher_: Teacher,
                                                     mocker: MockFixture,
                                                     summarizer_instance) -> None:
        one_day_later = datetime.datetime.now() + datetime.timedelta(days=1)
        mocker.patch('server.lib.Summarizer.generate_human_friendly_summary', return_value=None)
        with freeze_time(one_day_later):
            with pytest.raises(Exception):
                summarizer_instance(100)
                logs = summarizer_instance.processed_logs
                assert len(logs) == 10

    def test_get_crosstab_from_dims(self,
                                    teacher_: Teacher,
                                    mocker: MockFixture,
                                    school_class_logs,
                                    summarizer_instance) -> None:
        one_week_later = datetime.datetime.now() + datetime.timedelta(days=7)
        mocker.patch('server.lib.Summarizer.generate_human_friendly_summary', return_value=None)
        with freeze_time(one_week_later):
            summarizer_instance(7)
            crosstab = summarizer_instance.processed_crosstab
            assert crosstab.to_dict() == {
                'school_class': {
                    'create': 10
                }
            }

    def test_generate_human_friendly_summary(self, teacher_: Teacher,
                                             school_class_logs,
                                             summarizer_instance) -> None:
        one_week_later = datetime.datetime.now() + datetime.timedelta(days=7)
        with freeze_time(one_week_later):
            summarizer_instance(7)
            summarized_log = teacher_.activity_logs[-1]
            assert summarized_log.item_type == 'summarize_school_class'
            assert summarized_log.note == 'Created 10 School classes'
