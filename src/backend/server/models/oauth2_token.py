import time

from authlib.integrations.sqla_oauth2 import OAuth2TokenMixin
from server import db
from server.models.base_model import BaseModelMixin


class OAuth2Token(db.Model, OAuth2TokenMixin, BaseModelMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('teacher.id', ondelete='CASCADE'))
    user = db.relationship('Teacher')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()
