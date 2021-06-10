import re
from datetime import datetime
from typing import Optional

from server import db
from server.models.base_model import BaseModelMixin, unique_uuid4
from sqlalchemy import event
from sqlalchemy.dialects.postgresql import UUID

# Mappings
# Key Stage 3 (KS3): Year 7-9
# Key Stage 4 (KS4): Year 10-11
# Key Stage 5 (KS5): Year 12-13
KEYSTAGE_MAP = {
    'ks3': {
        'name': 'Key Stage 3 (KS3)',
        'range': {
            'start': 7,
            'end': 9
        }
    },
    'ks4': {
        'name': 'Key Stage 4 (KS4)',
        'range': {
            'start': 10,
            'end': 11
        }
    },
    'ks5': {
        'name': 'Key Stage 5 (KS5)',
        'range': {
            'start': 12,
            'end': 13
        }
    }
}


class SchoolClass(BaseModelMixin, db.Model):
    __tablename__ = "school_class"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, nullable=True)
    name = db.Column(db.String(256), nullable=False)

    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id"), nullable=True)
    subject = db.relationship('Subject')

    start_date = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow)
    exam_board = db.Column(db.String(256), nullable=True)
    key_stage = db.Column(db.String(256), nullable=True)
    teacher_id = db.Column(
        db.Integer, db.ForeignKey("teacher.id"), nullable=True)

    students = db.relationship(
        "Student", secondary="student_attended_class", viewonly=True
    )

    year_group = db.Column(db.String(256), nullable=True)

    quizzes = db.relationship("ClassQuiz",
                              backref="school_class",
                              cascade="all, delete",
                              lazy=True)

    def __init__(self,
                 name: str,
                 exam_board: str,
                 start_date: Optional['datetime'] = datetime.now(),
                 subject_id: Optional[int] = None,
                 teacher_id: Optional[int] = None,
                 year_group: Optional[str] = None,
                 uuid: Optional[UUID] = None,
                 key_stage: Optional[str] = None
                 ):
        self.name = name
        self.subject_id = subject_id
        self.exam_board = exam_board
        self.start_date = start_date
        self.teacher_id = teacher_id
        self.year_group = year_group
        if self.uuid is None:
            self.uuid = unique_uuid4()
        else:
            self.uuid = uuid
        self.key_stage = self.key_stage_from_year_group(year_group)

    def __repr__(self):
        return "<Classroom: %r>" % self.name

    def add_student(self, student):
        from .student_school_class import StudentAttendedClass

        StudentAttendedClass(student=student, school_class=self).save()

    def remove_student(self, student_id):
        from .student_school_class import StudentAttendedClass
        assoc_ = StudentAttendedClass.query\
                                     .filter_by(school_class=self,
                                                student_id=student_id)\
                                     .first()
        db.session.delete(assoc_)
        db.session.commit()

    def key_stage_from_year_group(self, year_group: str) -> str:
        year_group = year_group.lower()
        regex = re.compile(r'^Y|year\W([0-9]*)$')
        matched_year = int(regex.match(year_group)[1])
        if matched_year is None or matched_year == 0:
            return ''

        for (it_k, it_v) in KEYSTAGE_MAP.items():
            start = it_v['range']['start']
            end = it_v['range']['end']

            if matched_year >= start or matched_year <= end:
                return it_k
            else:
                continue
        return ''

    def has_student(self, student):
        from .student_school_class import StudentAttendedClass
        return StudentAttendedClass.query.filter_by(
            student=student,
            school_class=self).first() is not None

    def key_stage_for_front_end(self) -> str:
        if self.key_stage == '' or self.key_stage is None:
            return ''

        return KEYSTAGE_MAP.get(self.key_stage)['name']

    @classmethod
    def remove_classroom(cls, _class: 'SchoolClass'):
        db.engine.execute(
            "DELETE FROM student_attended_class WHERE school_class_id=%s",
            _class.id,
        )

        _class.delete()


@event.listens_for(SchoolClass, 'before_update')
def receive_set(mapper, connection, target):
    target.key_stage = target.key_stage_from_year_group(target.year_group)
