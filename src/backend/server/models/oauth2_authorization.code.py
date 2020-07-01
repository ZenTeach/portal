from authlib.integrations.sqla_oauth2 import OAuth2AuthorizationCodeMixin
from server import db
from server.models.base_model import BaseModelMixin


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin, BaseModelMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('teacher.id', ondelete='CASCADE'))
    user = db.relationship('Teacher')
