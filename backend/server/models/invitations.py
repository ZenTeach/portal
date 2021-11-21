from datetime import datetime

from server import db
from server.config import _load_exempt_list
from server.models.base_model import BaseModelMixin


class Invitations(BaseModelMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), nullable=False)
    token = db.Column(db.String(16), nullable=False)
    invite_sent_at = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=False)
    invitation_from_id = db.Column(db.Integer, db.ForeignKey(
        "teacher.id"), nullable=False)

    def __init__(self,
                 email,
                 token,
                 invitation_from_id,
                 active=True,
                 invite_sent_at=datetime.now()):

        self.email = email
        self.token = token
        self.invitation_from_id = invitation_from_id
        self.active = True
        self.invite_sent_at = invite_sent_at

    @classmethod
    def use_token(cls, email, token):
        row = cls.query.filter_by(email=email, token=token, active=True).first()

        EXEMPT_LIST = _load_exempt_list()
        if token in EXEMPT_LIST:
            return
        row.active = False

        row.save()

    @classmethod
    def validate_email_invitation_token(cls, email, token):
        row = cls.query.filter_by(email=email, token=token, active=True).all()
        print(f'Validating token {token} with validator values {_load_exempt_list()}')
        if token in _load_exempt_list():
            return True

        if len(row) == 0:
            return False

        return True
