import os
import re
from hashlib import md5
from pathlib import Path

import pytest
from factory import create_batch
from server.models import QuestionTypeEnum
from server.tests.factories import QuestionChoiceFactory, QuestionsFactory


def test_questions_model(client):
    """
        Smoke test
    """
    question = QuestionsFactory.build(multiple_choice_question_type=True)
    assert question.question_type == QuestionTypeEnum.multiple_choice


@pytest.mark.skip("Rethink mocking and model relationships")
def test_question_is_created_with_valid_correct_choice(client):
    pass


@pytest.mark.skip
def test_questions_enqueues_image_export(client,
                                         mocker,
                                         file_fixture_dir,
                                         build_question_with_choices,
                                         celery_app):

    test_image = os.path.join(file_fixture_dir, 'test_question_image.jpeg')

    def mock_path_name():
        return 'test_question_image.jpeg'

    mocker.patch('pathlib.Path.name', mock_path_name)

    def mock_upload_image_to_s3(image_name):
        img = Path(image_name)
        md5_hash = md5(img.name).hexdigest()  # nosec
        return "https://dummy-link.s3.eu-west-1.amazonaws.com/test_question_image_{}".format(md5_hash)  # noqa

    # mocker.patch('server.models.questions.upload_image_to_s3', mock_upload_image_to_s3)

    def mock_save_image_to_s3(mapper, connection, target):
        target.image_url = mock_upload_image_to_s3(test_image)
        return

    choices = create_batch(QuestionChoiceFactory, 4)

    question = QuestionsFactory.create(
        multiple_choice_question_type=True, choices=choices, image_url=test_image)

    assert True
    assert question
    url_regex = r'^https:\/\/([a-z0-9-_]*).s3.([a-z0-9-_]*).amazonaws.com\/([a-z0-9-_.]*)'
    assert re.match(url_regex, question.image_url)
