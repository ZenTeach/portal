import random
import string

from server import bcrypt, db
from server.models.base_model import BaseModelMixin
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID


def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(stringLength))  # nosec


class Student(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    firstname = db.Column(db.String(256), nullable=False)
    lastname = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False)

    classes = db.relationship(
        "SchoolClass", secondary="student_attended_class", viewonly=True
    )

    quiz_sessions = db.relationship(
        "ClassQuiz", secondary="quiz_session", viewonly=True
    )

    quiz_grades = db.relationship(
        "ClassQuiz", secondary="quiz_grade", viewonly=True)

    def __init__(
        self, firstname, lastname, email, classes=[], password=None, role="Student"
    ):
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        if password is None:
            self.password = bcrypt.generate_password_hash(randomString()).decode(
                "utf-8"
            )
        else:
            self.password = bcrypt.generate_password_hash(
                password).decode("utf-8")
        self.role = role
        self.classes = classes

    def __repr__(self) -> str:
        return "<Student %s>" % (self.firstname + " " + self.lastname)

    @property
    def full_name(self) -> str:
        return "{} {}".format(self.firstname, self.lastname)

    def add_quiz_score(self, quiz, response) -> None:
        from .quiz_grade import QuizGrade

        self.quiz_grade.append(
            QuizGrade(student=self, class_quiz=quiz, responses=response)
        )

    @classmethod
    def create_from_list(cls, lst) -> None:
        if len(lst) == 0:
            return
        errors = []
        instance = None
        added_students = []
        for it in lst:
            try:
                instance = cls(**it)
                instance.save()
            except Exception as e:
                errors.append(str(e))
            else:
                added_students.append(instance)
        return errors, added_students


@event.listens_for(Student.classes, "append")
def student_class_append_listener(target, value, initiator):
    if isinstance(value, list):
        [item.add_student(target) for item in value]
    else:
        value.add_student(target)

    target.save()


@event.listens_for(Student.classes, "remove")
def student_class_remove_listener(target, value, initiator):
    db.engine.execute(
        "DELETE FROM student_attended_class WHERE school_class_id=%s AND student_id=%s",
        value.id,
        target.id,
    )


@event.listens_for(Student.classes, 'dispose_collection')
def delete_student_classes(target, collection, collection_adapter):
    db.engine.execute(
        "DELETE FROM student_attended_class WHERE student_id=%s",
        target.id
    )
