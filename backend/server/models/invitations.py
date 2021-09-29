from datetime import datetime
from functools import lru_cache
from os import getcwd

from server import db
from server.models.base_model import BaseModelMixin
from yaml import load
from yamlloader.ordereddict import CLoader


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

        EXEMPT_LIST = cls._load_exempt_list()
        if token in EXEMPT_LIST:
            return
        row.active = False

        row.save()

    @classmethod
    @lru_cache(12)
    def _load_exempt_list(cls):
        data = None
        with open(f"{getcwd()}/server/exempt_list.yml") as fp:
            data = load(fp, Loader=CLoader)  # nosec

        return data

    @classmethod
    def validate_email_invitation_token(cls, email, token):
        row = cls.query.filter_by(email=email, token=token, active=True).all()

        if token in cls._load_exempt_list():
            return True

        if len(row) == 0:
            return False

        return True
