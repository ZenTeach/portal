from authlib.integrations.sqla_oauth2 import OAuth2ClientMixin
from server import db
from server.models.base_model import BaseModelMixin


class OAuth2Client(db.Model, OAuth2ClientMixin, BaseModelMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('teacher.id', ondelete='CASCADE'))
    user = db.relationship('Teacher')
