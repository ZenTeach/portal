
import os
from server.models import ClassQuiz, class_quiz_score, ClassQuizStatus, Questions, SchoolClass
from server import db
from sqlalchemy.orm import load_only
from sqlalchemy import update, and_
from functools import reduce
from itertools import accumulate

class Grader(object):
    # Takes a batch of administered quizzes and grades them
    # TODO: Add batching
    def __init__(self, school_class_id, batch=1):
        self.batch_size = batch
        self.school_class_id = school_class_id
        self.start_grading()

    @classmethod
    def from_quiz_session(cls, quiz_session_id):
        pass

    def start_grading(self):
        administered_quiz_list = ClassQuiz.query\
            .filter(\
                and_(ClassQuiz.status == ClassQuizStatus.administered.name\
                    , ClassQuiz.class_id == self.school_class_id)).all()

        print(f"Found {len(administered_quiz_list)} administered quizzes!")
        for quiz in administered_quiz_list:
            res = db.session.query(class_quiz_score).filter(class_quiz_score.columns['quiz_id']==quiz.id).all()
            print(f"Found {len(res)} submissions for quiz with id {quiz.id}")
            self._score_quiz(res, quiz)
            quiz.update_status(ClassQuizStatus.graded)

    def _score_quiz(self, quiz_submissions, quiz):
        for submission in quiz_submissions:
            # TODO: Add an sql model for class_quiz_score so it can be serialized
            # into a class
            data = submission[0][4]
            quiz_questions_id = list(map(lambda x: x["id"], quiz.questions))
            correct_choices_list = Questions.query\
                            .with_entities(Questions.id, Questions.correct_choice)\
                            .filter(Questions.id.in_(quiz_questions_id)).all()
            score = self._calculate_score(correct_choices_list, data)
            update_statement = class_quiz_score\
                            .update()\
                            .where(class_quiz_score.columns['quiz_id']==submission[0])\
                            .values(score=score)
            db.session.execute(update_statement)
            db.session.commit()
        # TODO: Step 2 get grade breakdown

    def _get_from_tuple_from_list(self, lst, val):
        return list(filter(lambda x: x[0] == int(val), lst))[0][1]

    def _calculate_score(self, correct_responses, submission_responses):
        cum_sum = 0
        for response in submission_responses:
            correct_choice = self._get_from_tuple_from_list(
                            correct_responses,
                            response['questionID'])

            if correct_choice == response['Choice_answer']:
                cum_sum += 1

        return cum_sum
