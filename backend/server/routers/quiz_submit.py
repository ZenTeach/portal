"""FastAPI port of ``server/api/quiz_submit_api.py``."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import exc, func

from server.models import ClassQuiz as ClassQuizModel
from server.models import QuizSession, QuizSessionStatus, Student
from server.routers.helpers import error_response, json_response, logger

quiz_submit_router = APIRouter(tags=["quiz-submit"])


class QuizSubmitArgs(BaseModel):
    """JSON body for ``POST /submit_quiz`` (mirrors ``quiz_submit_args``)."""

    StudentEmail: Optional[EmailStr] = None
    QuizId: Optional[UUID] = None
    data: List[Dict] = Field(default_factory=list)


@quiz_submit_router.get("/submit_quiz")
def submit_quiz_get(
    email: str = "",
    quiz: UUID = Query(...),
):
    """Creates a quiz session object."""
    student_email = email.lower()
    student = Student.query.filter(func.lower(Student.email) == student_email).first()
    class_quiz = ClassQuizModel.query.filter_by(uuid=quiz).first()
    success_response = {
        "message": "Created a new session!",
        "data": {},
        "status": "success",
    }

    if not student:
        # create an anonymous student if quiz is public
        if not class_quiz.private:
            student = Student.create_anonymous_student(
                classes=[class_quiz.school_class], confirmed=True
            )
            success_response["data"] = {
                "anonymous_student_email": student.email,
                "anonymous_student_password": "Asdfgh12!",
            }
        else:
            return error_response("Student email doesn't exist", 404)

    if not student.confirmed:
        return error_response("Email address hasn't been verified yet!", 400)

    if not class_quiz:
        return error_response("Class Quiz doesn't exist", 404)

    try:
        submission = QuizSession.query.filter_by(
            student=student, class_quiz=class_quiz
        ).first()
        if submission:
            if submission.has_session_ended():
                return error_response(
                    "Quiz has already been submitted. If you think this is by mistake, contact your teacher for a redo.",  # noqa
                    400,
                )
        else:
            new_session = class_quiz.add_student_session(student)
            class_quiz.save()
            if not class_quiz.private:
                # attach session to quiz response
                success_response["data"].update(
                    {"session_id": str(new_session.uuid)}
                )
    except exc.DatabaseError as e:
        logger.error(e)
        return json_response(
            {
                "message": "Couldn't create a new quiz session.",
                "status": "error",
            },
            500,
        )
    else:
        return json_response(success_response, 200)


@quiz_submit_router.post("/submit_quiz")
def submit_quiz_post(args: QuizSubmitArgs):
    StudentEmail = args.StudentEmail
    QuizId = args.QuizId
    data = args.data

    if len(data) == 0:
        return error_response(
            "Cannot submit quiz without any choices selected", 400
        )

    student = Student.query.filter_by(email=StudentEmail).first()
    class_quiz = ClassQuizModel.query.filter_by(uuid=QuizId).first()

    if student is None:
        return error_response(
            "Student with email {} doesn't exist".format(StudentEmail), 404
        )

    if class_quiz is None:
        return error_response("Class Quiz doesn't exist", 404)

    quiz_session = QuizSession.query.filter_by(
        student_id=student.id, class_quiz_id=class_quiz.id
    ).first()

    if not quiz_session:
        return error_response("Quiz not started", 404)

    try:
        if quiz_session.has_session_ended():
            return error_response("Session has ended!", 404)

        student.add_quiz_score(class_quiz, data)
        student.save()

        quiz_session.update_and_save(
            status=QuizSessionStatus.ended,
            end_time=datetime.now(),
        )

        return json_response(
            {"status": "success", "message": "Quiz submitted!"}, 201
        )
    except exc.IntegrityError as e:
        logger.error(e)
        return error_response("Encountered a server error", 500)
