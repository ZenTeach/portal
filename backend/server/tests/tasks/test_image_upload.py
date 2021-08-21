import os
import re

import pytest
from faker import Faker
from faker.providers import internet, lorem
from server.tasks import delete_image_from_s3, upload_image_to_s3
from server.tasks.image_upload import get_image_key
from vcr import VCR

fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)

vcr = VCR(
    serializer='yaml',
    cassette_library_dir='server/tests/fixtures/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)


class TestImageUpload:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    @pytest.mark.parametrize(
        "filename, regex",
        [
            pytest.param('cats.jpeg', r'^cats_(.*)\.jpeg$'),
            pytest.param('cat_and_dogs.png', r'^cat_and_dogs_(.*)\.png$'),
            pytest.param('pigs-in-a-sty.jpeg', r'^pigs-in-a-sty_(.*)\.jpeg')
        ]
    )
    def test_get_image_key(self, filename, regex):
        key = get_image_key(filename)
        assert re.match(regex, key)

    @pytest.mark.vcr
    @pytest.mark.block_network(allowed_hosts=["localhost", "redis", "::1"])
    @vcr.use_cassette()
    def test_upload_image_to_s3(self, file_fixture_dir):
        image_location = os.path.join(file_fixture_dir, "test_question_image.jpeg")
        url = upload_image_to_s3(image_location)
        url_regex = r'^https:\/\/([a-z0-9-_]*).s3.([a-z0-9-_]*).amazonaws.com\/([a-z0-9-_.]*)'
        assert url is not None
        assert re.match(url_regex, url)

    @pytest.mark.vcr
    @pytest.mark.block_network(allowed_hosts=["localhost", "redis", "::1"])
    @vcr.use_cassette()
    def test_delete_image_from_s3(self, client):
        o_id = '10991443cc42fcac84ac3e16f2ad3788'
        result = delete_image_from_s3(o_id)
        assert result is not None
