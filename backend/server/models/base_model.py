
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

    def reload(self):
        db.session.refresh(self)

    def update_from_dict(self, payload: dict) -> None:
        """
            update_from_dict
        """
        for item, value in payload.items():
            if not hasattr(self, item):
                raise Exception(f"Payload key {item} not found on model")

            self.__setattr__(item, value)


def unique_uuid4(x: Optional[UUID] = None) -> UUID:
    if x is None:
        x = uuid4()
    return x
