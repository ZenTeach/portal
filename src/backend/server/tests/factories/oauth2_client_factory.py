import json
import time

from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from faker.providers import date_time, internet, lorem, person
from server import db
from server.models import OAuth2Client
from werkzeug.security import gen_salt

fake = Faker()
fake.add_provider(person)
fake.add_provider(internet)
fake.add_provider(date_time)
fake.add_provider(lorem)


class OAuth2ClientFactory(SQLAlchemyModelFactory):
    class Meta:
        model = OAuth2Client
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    client_id = gen_salt(24)
    client_secret = gen_salt(48)
    client_id_issued_at = int(time.time())
    user = SubFactory('server.tests.factories.TeacherFactory')
    client_metadata = json.dumps({
        "client_name": fake.name(),
        "client_uri": fake.uri(),
        "grant_types": ['authorization_code', 'password'],
        "redirect_uris": [fake.uri()],
        "response_types": ['code'],
        "scope": ['profile'],
        "token_endpoint_auth_method": ['client_secret_basic']
    })
