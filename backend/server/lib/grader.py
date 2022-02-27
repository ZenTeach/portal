import json
import logging
from collections import namedtuple
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from server.models import (ClassQuiz, ClassQuizStatus, KnowledgeItem,
                           QuestionChoice, Questions, QuizGrade, QuizSession)
from sqlalchemy import and_

CorrectChoice = namedtuple("CorrectChoice", ["id", "correct_choice"])

logger = logging.getLogger(__name__)


class Feedback(object):
    def __init__(self):
        self._feedback = []
        self._is_correctly_answered = False

    @property
    def feedback(self) -> List:
        return self._feedback

    def _topic_exist_in_feedback(self, topic: str) -> bool:
        if len(self.feedback) == 0:
            return False
        return any([topic in x for x in self._feedback])

    def build_from_question_id(self,
                               topic_and_ki: Tuple[str, str],
                               choice_feedback: str,
                               is_correctly_answered: bool,
                               ki_qcount: dict) -> None:
        self._is_correctly_answered = is_correctly_answered
        self.build_for_topic(topic_and_ki[0])
        self.add_ki_to_topic(topic_and_ki[0], topic_and_ki[1])
        self.add_feedback_to_topic_and_ki(choice_feedback, topic_and_ki[0], topic_and_ki[1])
        self.compute_progress_for_topic_and_knowledge_item(
            topic_and_ki[0], topic_and_ki[1], ki_qcount)

    def build_for_topic(self, topic: str) -> Optional[dict]:
        if self._topic_exist_in_feedback(topic):
            return
        else:
            """
                structure
                feedback = {
                    'topic_a': {
                        'ki_a': {
                            'progress': '0/1' | '1/3',
                            'feedback': []
                        }
                    }
                }
            """
            interim = {
                topic: {}
            }
            self.feedback.append(interim)

    def _get_topic_breakdown(self, topic: str) -> Optional[Dict]:
        return next(
            iter(
                item for item in self._feedback if item.get(topic) is not None
            ),
            None)

    def _get_knowledgeitem_from_breakdown(self, topic: str, knowledge_item: str) -> Optional[Dict]:
        t_dict = self._get_topic_breakdown(topic)

        if t_dict is None:
            return None
        return t_dict[topic].get(knowledge_item, None)

    def add_ki_to_topic(self, topic: str, ki: str) -> None:
        if not self._topic_exist_in_feedback(topic):
            return
        m = self._get_topic_breakdown(topic)
        if ki in m[topic].keys():
            return
        else:
            m[topic][ki] = {}
            return

    def add_feedback_to_topic_and_ki(self, feedback: str, topic: str, ki: str):
        m = self._get_knowledgeitem_from_breakdown(topic, ki)
        if m is None:
            return

        if 'feedback' not in m:
            m['feedback'] = []

        if self._is_correctly_answered:
            return
        else:
            m["feedback"].append(feedback)
            return

    def compute_progress_for_topic_and_knowledge_item(self,
                                                      topic: str,
                                                      ki: str,
                                                      ki_qcount: dict) -> None:
        m = self._get_knowledgeitem_from_breakdown(topic, ki)
        if m is None:
            return

        if 'progress' not in m:
            m['progress'] = ''

        progress_ratio = m["progress"]
        if self._is_correctly_answered:
            if progress_ratio != '':
                nom, denom = list(map(int, progress_ratio.split('/')))
                nom = nom + 1
                progress_ratio = f'{nom}/{denom}'
            else:
                progress_ratio = f'1/{ki_qcount.get(ki)}'
        else:
            if progress_ratio == '':
                progress_ratio = f'0/{ki_qcount.get(ki)}'
        m['progress'] = progress_ratio

    def to_json(self) -> str:
        return json.dumps(self.feedback)


class Grader(object):
    # Takes a batch of administered quizzes and grades them
    # TODO: Add batching
    def __init__(self, school_class_id, class_quiz=None) -> None:
        self.batch_size = 1
        self.school_class_id = school_class_id
        self.class_quiz = class_quiz
        self._feedback_builder = Feedback()
        self.question_ki_count = {}
        self.start_grading()

    @classmethod
    def from_student_and_quiz_id(cls, student_id: int, class_quiz_id: int) -> None:
        quiz_grade = QuizGrade.query.filter_by(
            student_id=student_id, class_quiz_id=class_quiz_id).first()
        quiz_session = QuizSession.query.filter_by(
            student_id=student_id, class_quiz_id=class_quiz_id).first()

        if quiz_grade is None:
            raise ValueError('Quiz grade not found!')

        if quiz_session is None:
            raise ValueError('Quiz session not found!')

        quiz_grade.prepare_regrade_()
        cls.from_quiz_session(quiz_session.uuid)

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

        logger.debug(f"Found {len(administered_quiz_list)} administered quizzes!")
        for quiz in administered_quiz_list:
            res = QuizGrade.query.filter(
                QuizGrade.class_quiz_id == quiz.id).all()
            logger.debug(f"Found {len(res)} submissions for quiz with id {quiz.id}")
            self._score_quiz(res, quiz)

    def _get_question_count_per_ki_(self, quiz_questions: List[int]) -> Dict:
        indexed_results = {}
        results = Questions.query\
            .with_entities(KnowledgeItem.value, Questions.id)\
            .join(KnowledgeItem)\
            .filter(Questions.id.in_(quiz_questions))\
            .all()

        for (knowledge_item, question_id) in results:
            indexed_results[knowledge_item] = indexed_results.get(knowledge_item, 0) + 1

        return indexed_results

    def _score_quiz(self, quiz_submissions: List[QuizGrade], quiz: ClassQuiz) -> None:
        for submission in quiz_submissions:
            student_response = submission.responses
            quiz_questions_id = list(map(lambda x: x["id"], quiz.questions))
            self.question_ki_count = self._get_question_count_per_ki_(quiz_questions_id)
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
            score = self._calculate_score(correct_choices, student_response)
            logger.debug(f"Setting score for quiz {score}")
            submission.update_score(score)
            submission.is_graded()
            submission.update_grade_breakdown(self._feedback_builder.feedback)
            # teacher = self.class_quiz.school_class.teacher
            # ActivityLog.log(
            #     teacher,
            #     'create',
            #     'quiz_grade',
            #     submission.uuid,
            #     'note'
            # )

            del self._feedback_builder
            self._feedback_builder = Feedback()

    def _get_correct_choice_by_question_id(self,
                                           question_choice_uuid: UUID,
                                           haystack: Optional[List[CorrectChoice]] = None) -> Optional[str]:  # noqa
        if haystack is None:
            return

        indexable = list(filter(lambda value: question_choice_uuid ==
                         value.correct_choice, haystack))

        if len(indexable) == 0:
            return None
        logger.debug(f"Question is correctly answered {indexable}")
        return indexable[0][1]

    def _calculate_score(self,
                         correct_responses: List[CorrectChoice],
                         submission_responses: List[Dict]) -> int:
        cum_sum = 0
        for response in submission_responses:
            answered_correctly = self._get_correct_choice_by_question_id(
                UUID(response["Choice_answer"]), correct_responses
            )

            try:
                question = Questions.query.filter_by(id=response["questionID"]).first()
                topic_and_ki_tuple: Tuple[str, str] = (
                    question.topic.value, question.knowledge_item.value
                )
                choice_feedback: str = QuestionChoice.query\
                    .filter_by(uuid=UUID(response["Choice_answer"]))\
                    .first().feedback
                self._feedback_builder.build_from_question_id(
                    topic_and_ki_tuple,
                    choice_feedback,
                    answered_correctly is not None,
                    self.question_ki_count
                )
            except Exception as e:
                logger.error("Errored while building topic and knowledge-item pair", e)
                raise e

            if answered_correctly is None:
                logger.debug(
                    f"Found a question answered incorrectly: ids {response['questionID']}, {response['Choice_answer']}")  # noqa
            else:
                cum_sum += 1
        return cum_sum
