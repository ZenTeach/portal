import enum
import logging
from operator import itemgetter
from uuid import uuid4

from flask_sqlalchemy import BaseQuery
from marshmallow import INCLUDE, Schema, ValidationError, fields
from server import db
from server.lib import LocalImageStore
from server.models import QuestionChoice
from server.models.base_model import BaseModelMixin
from server.tasks import upload_image_to_s3
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.event import listens_for
from sqlalchemy_searchable import SearchQueryMixin
from sqlalchemy_utils.types import TSVectorType

# from werkzeug.utils import secure_filename

logger = logging.getLogger('model::question')


class QuestionsQuery(BaseQuery, SearchQueryMixin):
    pass


class QuestionTypeEnum(enum.Enum):
    multiple_choice = 1
    short_answer = 2
    long_answer = 3


class MultipleChoiceSchema(Schema):
    class Meta:
        unknown = INCLUDE

    a = fields.Str(required=True)
    b = fields.Str(required=True)
    c = fields.Str(required=True)
    d = fields.Str(required=True)


class Questions(BaseModelMixin, db.Model):
    __tablename__ = "questions"
    query_class = QuestionsQuery

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     nullable=False, default=uuid4())
    image_url = db.Column(db.Text, nullable=True)
    image = None
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(
        db.Enum(QuestionTypeEnum),
        nullable=False,
        default=QuestionTypeEnum.multiple_choice,
    )
    subject = db.Column(db.String(256), nullable=False)
    topic = db.Column(db.String(256), nullable=True)
    tag = db.Column(db.String(128), nullable=False)
    correct_choice_id = db.Column(db.Integer, nullable=False)
    choices = db.relationship("QuestionChoice", backref="question")
    knowledge_item = db.Column(db.String(256), nullable=False)
    search_vector = db.Column(TSVectorType("question"))

    def __init__(
        self,
        question,
        question_type,
        subject,
        topic,
        tag,
        knowledge_item,
        correct_choice_id,
        uuid=uuid4(),
        choices=[],
        image_url=""
    ):
        if question_type == QuestionTypeEnum.multiple_choice:
            try:
                MultipleChoiceSchema().validate(data=choices)
            except ValidationError:
                raise

        self.question = question
        self.question_type = question_type
        self.subject = subject
        self.topic = topic
        self.tag = tag
        self.knowledge_item = knowledge_item
        self.uuid = uuid
        self.correct_choice_id = correct_choice_id
        self.choices = choices
        self.image_url = image_url

    @classmethod
    def create_from_admin_form(cls, data):
        created_choice = []
        correct_choice_id = None
        for choice in data["choices"]:
            interim = QuestionChoice(
                choice["value"], choice["feedback"], choice["weight"], uuid4()
            )
            interim.save()
            if "is_correct_choice" in choice and correct_choice_id is None:
                correct_choice_id = interim.id
            created_choice.append(interim)

        image_name = None
        if 'image_url' in data and data['image_url'] is not None:
            image_file = data['image_url']
            # file_parts = image_file.filename.rsplit('.', 1)
            # secure_name = secure_filename("{}-{}.{}".format(
            #     file_parts[0].lower(),
            #     token_hex(6),
            #     file_parts[1].lower()
            # ))
            _, abs_filepath = itemgetter('url', 'abs_filepath')(LocalImageStore.save(image_file, None))  # noqa
            logger.info("Image absolute location: {}".format(abs_filepath))
            image_name = abs_filepath
            # image_file.save(image_tmp_location)
            # fp = open(image_name, 'wb')
            # fp.write(image_file.stream.read())
            # fp.close()

        instance = cls(
            data["question"],
            data["question_type"],
            data["subject"],
            data["topic"],
            data["tag"],
            data["knowledge_item"],
            correct_choice_id,
            uuid=uuid4(),
            choices=created_choice,
            image_url=image_name
        )
        instance.save()
        # instance.set_correct_choice()

    @classmethod
    def empty_instance(cls):
        return cls()

    def copy_image_to_tmp(self):
        pass


@listens_for(Questions, 'before_insert')
def save_image_to_s3(mapper, connection, target):
    # import pdb; pdb.set_trace()
    if target.image_url is None or target.image_url == '':
        return
    print("Inside after_insert hook")
    job_result = upload_image_to_s3.apply_async(args=[target.image_url])
    url = job_result.get()
    target.image_url = url
    # target.save()
