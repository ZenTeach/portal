
import os
from server.models import ClassQuiz, QuizGrade, ClassQuizStatus, Questions, SchoolClass, QuizSession
from server import db
from sqlalchemy.orm import load_only
from sqlalchemy import update, and_

class Grader(object):
    # Takes a batch of administered quizzes and grades them
    # TODO: Add batching
    def __init__(self, school_class_id, class_quiz=None, batch=1):
        self.batch_size = batch
        self.school_class_id = school_class_id
        self.class_quiz = class_quiz
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
            correct_choices_list = Questions.query\
                            .with_entities(Questions.id, Questions.correct_choice)\
                            .filter(Questions.id.in_(quiz_questions_id)).all()
            score = self._calculate_score(correct_choices_list, data)
            submission.update_score(score)
            submission.is_graded()
            submission.save()
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
