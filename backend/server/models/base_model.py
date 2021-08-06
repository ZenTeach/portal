
import logging
from typing import Optional
from uuid import UUID, uuid4

from server import db

logger = logging.getLogger(__name__)


class BaseModelMixin(object):
    """ Abstract class adding common functionalities """
    _IGNORED_COLUMNS = []

    def save(self, refresh=False):
        db.session.add(self)
        db.session.commit()

        if refresh:
            db.session.refresh(self)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def reload(self):
        db.session.refresh(self)

    def update_from_dict(self, payload: dict) -> None:
        """
            update_from_dict

            Updates the model from a dictionary.
        """
        for item, value in payload.items():
            if not hasattr(self, item):
                raise Exception(f"{self.__class__.__name__} does not have attribute {item}")
            else:
                if item not in self._IGNORED_COLUMNS:
                    self.__setattr__(item, value)

    def __iter__(self):
        table = self.__table__
        for key in table.columns.keys():
            if key not in table.primary_key and key not in self._IGNORED_COLUMNS:
                yield(key, getattr(self, key))


def unique_uuid4(x: Optional[UUID] = None) -> UUID:
    if x is None:
        x = uuid4()
    return x
