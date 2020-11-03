import os
import re
from operator import itemgetter
from secrets import token_hex

import pytest
from server.service import LocalImageFileStoreService
from werkzeug.datastructures import FileStorage

token_id = token_hex(6)


@pytest.fixture
def imageFileFixture(file_fixture_dir):
    return FileStorage(filename='test_question_image.jpeg')


@pytest.mark.parametrize(
    "actual_filename, public_id",
    [
        pytest.param("test_question_image.jpeg", None),
        pytest.param(f"test_question_image-{token_id}.jpeg",
                     f"test_question_image-{token_id}.jpeg")
    ]
)
def test_local_image_file_store_service_save_function(client,
                                                      mocker,
                                                      imageFileFixture,
                                                      actual_filename,
                                                      public_id):
    mocker.patch('werkzeug.datastructures.FileStorage.save')
    url, abs_filepath = itemgetter('url', 'abs_filepath')(
        LocalImageFileStoreService.save(imageFileFixture,
                                        public_id)
    )
    url_regex = re.compile(r'^/static/uploaded/([a-zA-Z0-9-_.]*)$')
    filepath_regex = re.compile(r'^/tmp/([a-zA-Z0-9-_.]*)$')

    assert actual_filename in url
    assert re.match(url_regex, url) is not None
    assert re.match(filepath_regex, abs_filepath) is not None


def test_local_image_file_store_service_remove_function(client, mocker, file_fixture_dir):
    mocker.patch('os.remove')
    path = os.path.join(file_fixture_dir, "test_question_image.jpeg")
    try:
        LocalImageFileStoreService.remove(path)
    except Exception as e:
        pytest.fail(e, pytrace=True)
