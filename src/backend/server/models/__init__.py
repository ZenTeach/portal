from marshmallow_enum import EnumField

from .class_quiz import ClassQuiz, ClassQuizStatus
from .student_school_class import StudentAttendedClass
from .school_class import SchoolClass
from .student import Student
from .teacher import Teacher
from .admin import Admin
from .quiz_grade import class_quiz_score
from .questions import Questions, QuestionTypeEnum
from .migrations.seeds import run_seed

__all__ = ['ClassQuiz', 'ClassQuizStatus', 'ClassQuizSchema', 'Teacher', 'TeacherSchema',
           'StudentAttendedClass', 'Student', 'StudentSchema',
           'SchoolClass', 'SchoolClassSchema', 'ClassQuizScore', 'Admin',
           'Questions', 'QuestionTypeEnum', 'QuestionsSchema', 'run_seed']

# serializers
from server import ma


class ClassQuizScoreSchema(ma.ModelSchema):
    class Meta:
        table = 'class_quiz_scores'


class QuestionsSchema(ma.ModelSchema):
    class Meta:
        model = Questions
        fields = ('id', 'question', 'question_type',
                  'subject', 'topic', 'knowledge_item', 'tag', 'choices')
    question_type = EnumField(QuestionTypeEnum, by_value=True)


class ClassQuizSchema(ma.ModelSchema):
    class Meta:
        model = ClassQuiz
    status = EnumField(ClassQuizStatus)


class StudentSchema(ma.ModelSchema):
    class Meta:
        model = Student
        fields = ('id', 'firstname', 'lastname', 'email',
                  'date_of_birth', 'role', 'classes')
    classes = ma.List(ma.HyperlinkRelated(
        "school_class.schoolclass", url_key="school_class_id"))


class SchoolClassSchema(ma.ModelSchema):
    class Meta:
        model = SchoolClass
        fields = ('id', 'name', 'subject', 'start_date', 'students', 'quizzes')

    quizzes = ma.Nested(ClassQuizSchema, many=True)
    students = ma.Nested(StudentSchema, many=True)


class TeacherSchema(ma.ModelSchema):
    class Meta:
        fields = ('id', 'firstname', 'lastname', 'email',
                  'date_of_birth', 'role', 'classes')
        model = Teacher

    classes = ma.Nested(SchoolClassSchema, many=True)
