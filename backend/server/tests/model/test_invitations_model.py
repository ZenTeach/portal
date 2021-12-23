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


@pytest.fixture
def invited_teacher_(client: FlaskClient) -> Teacher:
    return TeacherFactory(with_school_class=True,  # nosec
                          email="nextjoemama@example.com", password="Asdfgh12!")


@pytest.fixture(scope='function')
def invitations(teacher_: Teacher, invited_teacher_: Teacher) -> Invitations:
    invite = Invitations(invited_teacher_.email, token_hex(8), teacher_.id)
    invite.save()
    return invite


def test_invitations_instance(client: FlaskClient,
                              invitations: Invitations,
                              invited_teacher_: Teacher) -> None:
    assert invited_teacher_.email
    assert invitations.token
    assert invitations.invitation_from_id

    assert Invitations.validate_email_invitation_token(invited_teacher_.email, invitations.token)

    assert invitations.active
    Invitations.use_token(invited_teacher_.email, invitations.token)
    assert not invitations.active


def test_invitee_association(client: FlaskClient,
                             invitations: Invitations,
                             invited_teacher_: Teacher) -> None:
    assert invitations.active
    Invitations.use_token(invited_teacher_.email, invitations.token)
    assert not invitations.active
    Invitations.associate_invitee(invited_teacher_, invitations.token)
    assert invitations.invitee.email == invited_teacher_.email
