
import os
from server.models import ClassQuiz,\
     QuizGrade, ClassQuizStatus, Questions, \
     SchoolClass, QuizSession, QuestionChoice
from server import db
from sqlalchemy.orm import load_only
from sqlalchemy import update, and_
from uuid import UUID
from collections import namedtuple
import json
CorrectChoice = namedtuple('CorrectChoice', ['id', 'correct_choice'])

class Feedback(object):
    def __init__(self):
        self._feedback = []

    @property
    def feedback(self):
        return self._feedback

    def _topic_exist_in_feedback(self, topic):
        if len(self._feedback) == 0:
            return False
        return len(list(filter(lambda x: x["topic"] == topic, self._feedback))) != 0

    def build_from_question_id(self, questionID, choiceID):
        _tuple = Questions.query\
            .with_entities(Questions.topic, Questions.knowledge_item)\
            .filter_by(id=questionID).first()
        self.build_for_topic(_tuple[0])
        self.add_ki_to_topic(_tuple[0], _tuple[1])
        self.add_feedback_to_topic(choiceID, _tuple[0])
        self.compute_progress_for_topic(_tuple[0])

    def build_for_topic(self, topic):
        if self._topic_exist_in_feedback(topic):
            return
        else:
            interim = {
                "topic": topic,
                "knowledge_item": [],
                "progress": [],
                "feedback": []
            }
            self._feedback.append(interim)

    def _get_topic_breakdown(self, topic):
        return next(iter(item for item in self._feedback if item["topic"] == topic), None)

    def _get_feedback_for_choice(self, choice_id):
        choice = QuestionChoice.query.filter_by(uuid=choice_id).first()
        return choice.feedback.content

    def add_ki_to_topic(self, topic, ki):
        if not self._topic_exist_in_feedback(topic):
            return
        m = self._get_topic_breakdown(topic)
        if m is None:
            return
        m["knowledge_item"].append(ki)

    def add_feedback_to_topic(self, choiceID, topic):
        feedback = self._get_feedback_for_choice(choiceID)
        m = self._get_topic_breakdown(topic)
        if m is None:
            return
        m["feedback"].append(feedback)

    def compute_progress_for_topic(self, topic):
        m = self._get_topic_breakdown(topic)
        m["progress"].append("0/1")

    def to_json(self):
        return json.dumps(self._feedback)

class Grader(object):
    # Takes a batch of administered quizzes and grades them
    # TODO: Add batching
    def __init__(self, school_class_id, class_quiz=None, batch=1):
        self.batch_size = batch
        self.school_class_id = school_class_id
        self.class_quiz = class_quiz
        self._feedback_builder = Feedback()
        self.start_grading()

    @classmethod
    def from_quiz_session(cls, quiz_session_id):
        # Get submission from session
        session = QuizSession.query.filter_by(uuid=quiz_session_id).first()
        if not session:
            raise Exception("Quiz session not found")

        # get submission
        quiz = session.class_quiz
        student = session.student

        cls(quiz.class_id, quiz)

    def start_grading(self):
        if self.class_quiz:
            administered_quiz_list = [self.class_quiz]
        else:
            administered_quiz_list = ClassQuiz.query\
                .filter(\
                    and_(ClassQuiz.status == ClassQuizStatus.administered.name\
                        , ClassQuiz.class_id == self.school_class_id)).all()

        print(f"Found {len(administered_quiz_list)} administered quizzes!")
        for quiz in administered_quiz_list:
            res = QuizGrade.query.filter(QuizGrade.class_quiz_id==quiz.id).all()
            print(f"Found {len(res)} submissions for quiz with id {quiz.id}")
            self._score_quiz(res, quiz)

    def _score_quiz(self, quiz_submissions, quiz):
        for submission in quiz_submissions:
            data = submission.responses
            quiz_questions_id = list(map(lambda x: x["id"], quiz.questions))
            correct_choices_resultset = Questions.query\
                            .with_entities(Questions.id, Questions.correct_choice)\
                            .filter(Questions.id.in_(quiz_questions_id)).all()
            correct_choices = [CorrectChoice._make([vals.id, vals.correct_choice]) for vals in correct_choices_resultset]
            score = self._calculate_score(correct_choices, data)
            submission.update_score(score)
            submission.is_graded()
            # TODO: Step 2 get grade breakdown
            submission.update_grade_breakdown(self._feedback_builder.feedback)

    def _get_from_tuple_from_list(self, lst, val):
        return list(filter(lambda x: x.id == int(val), lst))[0][1]

    def _calculate_score(self, correct_responses, submission_responses):
        cum_sum = 0
        for response in submission_responses:
            correct_choice = self._get_from_tuple_from_list(
                            correct_responses,
                            response['questionID'])
            if UUID(str(correct_choice)) == UUID(response['Choice_answer']):
                cum_sum += 1
            else:
                #TODO: build feedback
                self._feedback_builder.build_from_question_id(response['questionID'], response['Choice_answer'])
        return cum_sum
