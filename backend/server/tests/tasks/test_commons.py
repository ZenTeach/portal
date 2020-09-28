from faker import Faker
from faker.providers import internet, lorem

fake = Faker()
fake.add_provider(internet)
fake.add_provider(lorem)


class TestCommons:
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass
