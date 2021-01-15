from secrets import token_hex

import pytest
from faker import Faker
from faker.providers import internet
from flask.testing import FlaskClient
from server.models import Invitations, Teacher
from server.tests.factories import TeacherFactory

fake = Faker()
fake.add_provider(internet)


@pytest.fixture
def teacher_(client: FlaskClient) -> Teacher:
    return TeacherFactory(with_school_class=True,  # nosec
                          email="joemama@example.com", password="Asdfgh12!")


@pytest.fixture(scope='function')
def invitations(teacher_: Teacher):
    invite = Invitations(fake.safe_email(), token_hex(8), teacher_.id)
    invite.save()
    return invite


def test_invitations_instance(client: FlaskClient, invitations: Invitations):
    assert invitations.email
    assert invitations.token
    assert invitations.invitation_from_id

    assert Invitations.validate_email_invitation_token(invitations.email, invitations.token)

    assert invitations.active == True  # noqa
    Invitations.use_token(invitations.email, invitations.token)
    assert invitations.active == False  # noqa
