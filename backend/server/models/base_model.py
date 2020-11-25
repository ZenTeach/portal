
from typing import Optional
from uuid import UUID, uuid4

from server import db


class BaseModelMixin(object):
    """ Abstract class adding common functionalities """

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


def unique_uuid4(x: Optional[UUID] = None) -> UUID:
    if x is None:
        x = uuid4()
    return x
