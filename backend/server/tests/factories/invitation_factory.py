from secrets import token_hex

from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import internet
from server import db
from server.models import Invitations

fake = Faker()
fake.add_provider(internet)


class InvitationFactory(SQLAlchemyModelFactory):
    class Meta:
        model = Invitations
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    token = token_hex(8)
    email = fake.safe_email()
    invitation_from_id = None
