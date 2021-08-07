import logging
from typing import List

from server import db  # noqa
from server.models import KnowledgeItem, Questions, QuizGrade, Topic
from server.tasks import regrade_quiz

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

        question._knowledge_item = knowledge_item
        question._knowledge_item_id = knowledge_item.id
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

        question._topic = topic
        question._topic_id = topic.id
        question.save()
    logger.info("Update complete")
