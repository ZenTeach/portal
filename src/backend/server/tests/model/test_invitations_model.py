from secrets import token_hex

import pytest
from faker import Faker
from faker.providers import internet
from server.models import Invitations

fake = Faker()
fake.add_provider(internet)


@pytest.fixture(scope='function')
def invitations(teacher):
    invite = Invitations(fake.safe_email(), token_hex(8), teacher.id)
    invite.save()
    return invite


def test_invitations_instance(client, invitations):
    assert invitations.email
    assert invitations.token
    assert invitations.invitation_from_id


def test_invitations_validate_email_invitation_token(client, teacher, invitations):
    assert Invitations.validate_email_invitation_token(invitations.email, invitations.token)
