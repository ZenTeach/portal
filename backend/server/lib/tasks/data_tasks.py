import datetime
import logging
from typing import List

from server import db  # noqa
from server.models import (ClassQuiz, ClassQuizStatus, KnowledgeItem,
                           Questions, QuizGrade, Topic)
from server.tasks import regrade_quiz
from sqlalchemy import Date, cast

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

__all__ = ['trigger_quiz_regrading',
           'trigger_knowledge_item_migration',
           'trigger_topic_migration']


def trigger_quiz_regrading():
    for quiz_grade in QuizGrade.query.all():
        # enqueue regrade_quiz jobs for all quiz grades
        regrade_quiz.apply_async(args=[quiz_grade.class_quiz_id, quiz_grade.student_id])


def trigger_knowledge_item_migration() -> None:
    questions: List[Questions] = Questions.query.all()
    logger.info(f"Updating {len(questions)} Questions")
    for question in questions:
        knowledge_item = KnowledgeItem.query.filter_by(value=question.knowledge_item).first()
        if not knowledge_item:
            logger.info(
                f"Couldn't find KnowledgeItem with value {question.knowledge_item}. Creating...")
            knowledge_item = KnowledgeItem(value=question.knowledge_item)
            knowledge_item.save()
        else:
            knowledge_item.subject_id = question.subject_id

        question.knowledge_item = knowledge_item
        question.knowledge_item_id = knowledge_item.id

        topic = Topic.query.filter_by(value=question.topic).first()
        if topic:
            logger.info("Setting the topic..")
            knowledge_item.topic_id = topic.id
        else:
            logger.warn(
                f"Topic {question.topic} was not found in the database.\
                Re-run this task to ensure that the knowledge items are updated.")
        question.save()
    logger.info("Update complete")


def trigger_topic_migration() -> None:
    questions: List[Questions] = Questions.query.all()
    logger.info(f"Updating {len(questions)} Questions")
    for question in questions:
        topic = Topic.query.filter_by(value=question.topic).first()
        if not topic:
            logger.info(f"Couldn't find Topic with value {question.topic}. Creating...")
            topic = Topic(value=question.topic)
            topic.save()
        else:
            topic.subject_id = question.subject_id

        question.topic = topic
        question.topic_id = topic.id
        question.save()
    logger.info("Update complete")


def mark_grades_sent_for_old_quizzes() -> None:
    """
        Set quiz grade result_sent to true for quizzes older than 1 wk
    """
    one_week_later = datetime.datetime.now() + datetime.timedelta(days=7)
    affected_quiz_grade_ids = QuizGrade.query.join(ClassQuiz).with_entities(
        QuizGrade.id
    ).filter(
        ClassQuiz.status == ClassQuizStatus.administered
    ).filter(
        QuizGrade.result_sent == False  # noqa
    ).filter(
        cast(ClassQuiz.created, Date) > one_week_later
    ).all()
    logger.info(f"Found {len(affected_quiz_grade_ids)} old quiz grades.")

    QuizGrade.query.update().where(
        QuizGrade.id.in_(affected_quiz_grade_ids)
    ).values({'result_sent': True})
