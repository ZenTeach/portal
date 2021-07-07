import json
import logging
from collections import namedtuple
from typing import Dict, List, Optional
from uuid import UUID

from server.models import (ClassQuiz, ClassQuizStatus, QuestionChoice,
                           Questions, QuizGrade, QuizSession)
from sqlalchemy import and_

CorrectChoice = namedtuple("CorrectChoice", ["id", "correct_choice"])

logger = logging.getLogger(__name__)


class Feedback(object):
    def __init__(self):
        self._feedback = []

    @property
    def feedback(self) -> List:
        return self._feedback

    def _topic_exist_in_feedback(self, topic: str) -> bool:
        if len(self._feedback) == 0:
            return False
        filtered_topic = [x["topic"] == topic for x in self._feedback]
        return len(filtered_topic) != 0

    def build_from_question_id(self, questionID: int, choiceID: UUID) -> None:
        _tuple = (
            Questions.query.with_entities(
                Questions.topic, Questions.knowledge_item)
            .filter_by(id=questionID)
            .first()
        )
        self.build_for_topic(_tuple[0])
        self.add_ki_to_topic(_tuple[0], _tuple[1])
        self.add_feedback_to_topic(choiceID, _tuple[0])
        self.compute_progress_for_topic(_tuple[0])

    def build_for_topic(self, topic: str) -> None:
        if self._topic_exist_in_feedback(topic):
            return
        else:
            interim = {
                "topic": topic,
                "knowledge_item": [],
                "progress": [],
                "feedback": [],
            }
            self._feedback.append(interim)

    def _get_topic_breakdown(self, topic: str) -> Optional[Dict]:
        return next(
            iter(
                item for item in self._feedback if item["topic"] == topic
            ),
            None)

    def _get_feedback_for_choice(self, choice_id: UUID) -> str:
        choice = QuestionChoice.query.filter_by(uuid=choice_id).first()
        return choice.feedback

    def add_ki_to_topic(self, topic: str, ki: str) -> None:
        if not self._topic_exist_in_feedback(topic):
            return
        m = self._get_topic_breakdown(topic)
        if m is None:
            return
        m["knowledge_item"].append(ki)

    def add_feedback_to_topic(self, choiceID: UUID, topic: str):
        feedback = self._get_feedback_for_choice(choiceID)
        m = self._get_topic_breakdown(topic)
        if m is None:
            return
        m["feedback"].append(feedback)

    def compute_progress_for_topic(self, topic: str) -> None:
        m = self._get_topic_breakdown(topic)
        if m is None:
            return
        m["progress"].append("0/1")

    def to_json(self) -> str:
        return json.dumps(self._feedback)


class Grader(object):
    # Takes a batch of administered quizzes and grades them
    # TODO: Add batching
    def __init__(self, school_class_id, class_quiz=None) -> None:
        self.batch_size = 1
        self.school_class_id = school_class_id
        self.class_quiz = class_quiz
        self._feedback_builder = Feedback()
        self.start_grading()

    @classmethod
    def from_quiz_session(cls, quiz_session_id: UUID) -> None:
        # Get submission from session
        session = QuizSession.query.filter_by(uuid=quiz_session_id).first()
        if not session:
            raise Exception("Quiz session not found")

        # get submission
        quiz = session.class_quiz

        cls(quiz.class_id, quiz)

    def start_grading(self):
        if self.class_quiz:
            administered_quiz_list = [self.class_quiz]
        else:
            administered_quiz_list = ClassQuiz.query.filter(
                and_(
                    ClassQuiz.status == ClassQuizStatus.administered.name,
                    ClassQuiz.class_id == self.school_class_id,
                )
            ).all()

        logger.info(f"Found {len(administered_quiz_list)} administered quizzes!")
        for quiz in administered_quiz_list:
            res = QuizGrade.query.filter(
                QuizGrade.class_quiz_id == quiz.id).all()
            logger.info(f"Found {len(res)} submissions for quiz with id {quiz.id}")
            self._score_quiz(res, quiz)

    def _score_quiz(self, quiz_submissions: List[QuizGrade], quiz: ClassQuiz) -> None:
        for submission in quiz_submissions:
            # TODO: There are two issues with working with unvalidated
            # input. One, the quiz submission can be flawed if they're referencing
            # invalid/inexistent question. Second, the class quiz itself can contain
            # flawed/inconsistent question ids if there's no validation.
            #  Possible solution, add validation when creating quizzes.
            data = submission.responses
            quiz_questions_id = list(map(lambda x: x["id"], quiz.questions))

            correct_choices_resultset = (
                Questions.query.with_entities(Questions.id, QuestionChoice.uuid)
                               .filter(and_(Questions.correct_choice_id == QuestionChoice.id,
                                            Questions.id.in_(quiz_questions_id)))
                               .order_by(Questions.id)
                               .all()
            )

            correct_choices = [
                CorrectChoice._make([vals.id, vals.uuid])
                for vals in correct_choices_resultset
            ]
            score = self._calculate_score(correct_choices, data)
            submission.update_score(score)
            submission.is_graded()
            # TODO: Step 2 get grade breakdown
            submission.update_grade_breakdown(self._feedback_builder.feedback)

    def _get_correct_choice_by_question_id(self,
                                           question_choice_uuid: UUID,
                                           haystack: Optional[List[CorrectChoice]] = None) -> Optional[str]:  # noqa
        if haystack is None:
            return

        _filtered = filter(lambda value: question_choice_uuid == value.correct_choice, haystack)
        indexable = list(_filtered)

        if len(indexable) == 0:
            return None

        return indexable[0][1]

    def _calculate_score(self,
                         correct_responses: List[CorrectChoice],
                         submission_responses: List[Dict]) -> int:
        cum_sum = 0
        for response in submission_responses:
            answered_correctly = self._get_correct_choice_by_question_id(
                UUID(response["Choice_answer"]), correct_responses
            )

            if answered_correctly is None:
                self._feedback_builder.build_from_question_id(
                    int(response["questionID"]), UUID(response["Choice_answer"])
                )
            else:
                cum_sum += 1

        return cum_sum
