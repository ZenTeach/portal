import time

from faker import Faker
from faker.providers import internet, lorem
from flask import g
from flask_mail import Message
from server.tasks.commons import send_mail

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

    def test_send_main(self, client):
        # import pdb; pdb.set_trace()  # noqa
        send_mail(Message(
            sender="tester@zenteach.co.uk",
            recipients=[fake.ascii_email()],
            subject=fake.sentence(),
            body=fake.paragraph()
        ))
        time.sleep(1)
        assert g.outbox.length != 0
